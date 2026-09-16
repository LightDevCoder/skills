(() => {
  "use strict";
  const names = ["settings", "travelers", "bills", "todos", "tickets"];
  const adapters = new Set();
  const clone = (value) => JSON.parse(JSON.stringify(value));
  const emptySnapshot = () => ({
    version: 1,
    revision: 0,
    settings: null,
    travelers: [],
    bills: [],
    todos: [],
    tickets: [],
  });
  const normalizeSnapshot = (raw) => ({ ...emptySnapshot(), ...(raw || {}) });
  function notify(status, message) {
    if (typeof window !== "undefined")
      window.dispatchEvent(
        new CustomEvent("light:sync-status", { detail: { status, message } }),
      );
  }
  function normalizeApiBase(value = "/api/trip") {
    if (!/^\/(?!\/)/.test(value) || /[\\?#]/.test(value))
      throw new Error("API must be same-origin");
    return value.replace(/\/+$/, "");
  }
  function createD1Adapter(options = {}) {
    if (!/^[a-zA-Z0-9_-]{1,100}$/.test(options.tripId || ""))
      throw new Error("A trip ID is required");
    const owned = options.collections;
    if (
      !Array.isArray(owned) ||
      !owned.length ||
      owned.some((x) => !names.includes(x))
    )
      throw new Error("Explicit collection allowlist required");
    const endpoint = `${normalizeApiBase(options.apiBase)}/${encodeURIComponent(options.tripId)}`;
    const pendingKey = `light-pending:${options.tripId}:${[...owned].sort().join(",")}`;
    const journal =
      options.journal ||
      (typeof sessionStorage !== "undefined" ? sessionStorage : null);
    let observed = null,
      pending = journal
        ? JSON.parse(journal.getItem(pendingKey) || "null")
        : null,
      busy = false;
    const persistPending = () => {
      if (journal) {
        if (pending) journal.setItem(pendingKey, JSON.stringify(pending));
        else journal.removeItem(pendingKey);
      }
    };
    async function request(method, body) {
      const response = await fetch(endpoint, {
        method,
        credentials: "same-origin",
        cache: "no-store",
        headers: body ? { "content-type": "application/json" } : {},
        ...(body ? { body: JSON.stringify(body) } : {}),
        signal: AbortSignal.timeout(15000),
      });
      let data;
      try {
        data = await response.json();
      } catch {
        throw new Error("服务器未返回有效数据，请重新登录或重试。");
      }
      if (!response.ok) {
        const error = new Error(data.error || `HTTP ${response.status}`);
        error.status = response.status;
        throw error;
      }
      return normalizeSnapshot(data);
    }
    async function executePending() {
      if (busy) throw new Error("正在保存，请稍候。");
      if (!pending) return observed;
      busy = true;
      notify("saving", "正在保存到共享旅程…");
      try {
        observed = await request("POST", pending);
        pending = null;
        // A failed local cleanup cannot turn a confirmed server commit into a
        // failed save. A surviving journal entry can safely replay its receipt.
        try { persistPending(); } catch {}
        busy = false;
        notify("saved", "已同步到共享旅程");
        return clone(observed);
      } catch (error) {
        // Authentication happens before receipt lookup, so it cannot establish
        // whether an earlier uncertain request committed. Keep its exact body.
        if (error.status && error.status < 500 && ![401, 403].includes(error.status)) {
          pending = null;
          try { persistPending(); } catch {}
        }
        notify(
          error.status === 409 ? "conflict" : "error",
          error.status === 409
            ? "同行者已修改内容。请刷新共享数据，再检查并保存你的修改。"
            : `${error.message} 未确认的保存可用“重试保存”恢复。`,
        );
        throw error;
      } finally {
        busy = false;
      }
    }
    const api = {
      mode: "d1",
      tripId: options.tripId,
      get pending() {
        return Boolean(pending);
      },
      get busy() {
        return busy;
      },
      async load() {
        if (busy || pending)
          throw new Error("上次保存尚未确认，请先重试保存。");
        try {
          observed = await request("GET");
          return clone(observed);
        } catch (error) {
          notify("error", error.message);
          throw error;
        }
      },
      async save(snapshot) {
        if (!observed) throw new Error("共享数据尚未成功读取，请先刷新。");
        if (pending || busy)
          throw new Error("请先重试上次保存，不要重复提交。");
        const next = normalizeSnapshot(snapshot),
          changes = [];
        for (const collection of owned) {
          if (collection === "settings") {
            if (
              JSON.stringify(next.settings) !==
              JSON.stringify(observed.settings)
            )
              changes.push({
                collection,
                id: "settings",
                op: next.settings ? "upsert" : "delete",
                ...(next.settings ? { value: next.settings } : {}),
              });
          } else {
            const before = new Map(observed[collection].map((x) => [x.id, x]));
            const after = new Map(next[collection].map((x) => [x.id, x]));
            for (const [id] of before)
              if (!after.has(id))
                changes.push({ collection, id, op: "delete" });
            for (const [id, value] of after)
              if (JSON.stringify(value) !== JSON.stringify(before.get(id)))
                changes.push({ collection, id, op: "upsert", value });
          }
        }
        if (!changes.length) return clone(observed);
        pending = {
          mutationId: crypto.randomUUID(),
          expectedRevision: observed.revision,
          changes,
        };
        try {
          persistPending();
        } catch {
          pending = null;
          notify(
            "error",
            "浏览器无法保存恢复记录，本次未发送。请释放存储后重试。",
          );
          throw new Error("无法保存恢复记录");
        }
        const result = await executePending();
        Object.assign(snapshot, result);
        return result;
      },
      async applyChange(collection, value, op = "upsert") {
        if (!owned.includes(collection))
          throw new Error("Collection is not enabled");
        if (!observed) throw new Error("请先读取共享数据");
        const next = clone(observed);
        if (collection === "settings")
          next.settings = op === "delete" ? null : value;
        else {
          next[collection] = next[collection].filter((x) => x.id !== value.id);
          if (op === "upsert") next[collection].push(value);
        }
        return api.save(next);
      },
      retry: executePending,
    };
    adapters.add(api);
    return api;
  }
  function createLocalAdapter(options = {}) {
    const key = `light-travelpage:v1:${options.tripId}`;
    const storage = options.storage || globalThis.localStorage;
    const owned = options.collections || names;
    const load = async () =>
      normalizeSnapshot(JSON.parse(storage.getItem(key) || "null"));
    return {
      mode: "local",
      tripId: options.tripId,
      storageKey: key,
      load,
      async save(snapshot) {
        const current = await load();
        for (const name of owned) current[name] = clone(snapshot[name]);
        storage.setItem(key, JSON.stringify(current));
        Object.assign(snapshot, current);
        return current;
      },
      async applyChange(collection, value, op = "upsert") {
        const current = await load();
        if (collection === "settings")
          current.settings = op === "delete" ? null : value;
        else {
          current[collection] = current[collection].filter(
            (x) => x.id !== value.id,
          );
          if (op === "upsert") current[collection].push(value);
        }
        return this.save(current);
      },
    };
  }
  const publicApi = {
    emptySnapshot,
    normalizeSnapshot,
    normalizeApiBase,
    createD1Adapter,
    createLocalAdapter,
    createAdapter(options) {
      if (options.mode === "d1") return createD1Adapter(options);
      if (options.mode === "local") return createLocalAdapter(options);
      throw new Error("Persistence mode required");
    },
    hasPending() {
      return [...adapters].some((x) => x.pending || x.busy);
    },
    async retryAll() {
      const recovered = [];
      for (const adapter of adapters) if (adapter.pending) {
        try {
          const snapshot = await adapter.retry();
          recovered.push({ adapter, snapshot });
        } catch (error) {
          recovered.push({ adapter, error });
        }
      }
      return recovered;
    },
    async exportSnapshot(options) {
      const adapter = createD1Adapter({ ...options, collections: names });
      try {
        return {
          format: "light-travelpage-backup-v1",
          tripId: options.tripId,
          exportedAt: new Date().toISOString(),
          snapshot: await adapter.load(),
        };
      } finally {
        adapters.delete(adapter);
      }
    },
    async restoreSnapshot(options, backup, expectedRevision) {
      if (
        backup?.format !== "light-travelpage-backup-v1" ||
        backup.tripId !== options.tripId
      )
        throw new Error("备份不属于当前旅程");
      const snapshot = backup.snapshot;
      if (!snapshot || typeof snapshot !== "object" || Array.isArray(snapshot) || snapshot.version !== 1 || !Number.isSafeInteger(snapshot.revision) || snapshot.revision < 0 || !Object.hasOwn(snapshot,"settings") || (snapshot.settings !== null && (typeof snapshot.settings !== "object" || Array.isArray(snapshot.settings))) || names.filter(name => name !== "settings").some(name => !Array.isArray(snapshot[name]) || snapshot[name].some(record => !record || typeof record !== "object" || !record.id))) throw new Error("备份结构不完整或版本不受支持；未发送任何恢复请求");
      const adapter = createD1Adapter({ ...options, collections: names });
      try {
        const current = await adapter.load();
        if (current.revision !== expectedRevision)
          throw new Error("云端已变化，请重新检查后恢复");
        return await adapter.save(backup.snapshot);
      } finally {
        if (!adapter.pending) adapters.delete(adapter);
      }
    },
  };
  if (typeof module === "object" && module.exports) module.exports = publicApi;
  if (typeof window !== "undefined") window.TravelRuntimeStorage = publicApi;
})();
