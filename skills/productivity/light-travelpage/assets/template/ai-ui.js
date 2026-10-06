(() => {
  "use strict";
  function createAiController({ tripId, journal, fetchImpl = fetch, refresh = async () => {} }) {
    if (!/^[A-Za-z0-9_-]{1,100}$/.test(tripId || "")) throw new Error("旅程 ID 无效");
    if (!journal) throw new Error("浏览器无法保留恢复记录");
    const key = `light-ai-pending:${tripId}`;
    let pending = JSON.parse(journal.getItem(key) || "null"), busy = false;
    const persist = () => pending ? journal.setItem(key, JSON.stringify(pending)) : journal.removeItem(key);
    async function request(url, options) {
      const response = await fetchImpl(url, { credentials: "same-origin", cache: "no-store", ...options });
      let data;
      try { data = await response.json(); } catch { throw new Error("服务器未返回有效数据，请重新登录或重试"); }
      if (!response.ok) { const error = new Error(data.error || `HTTP ${response.status}`); error.status = response.status; throw error; }
      return data;
    }
    async function execute() {
      if (busy) throw new Error("正在处理，请稍候");
      if (!pending) throw new Error("没有待重试的请求");
      busy = true;
      try {
        const result = await request(`/api/ai/${encodeURIComponent(tripId)}`, {
          method: "POST", headers: { "content-type": "application/json" },
          body: JSON.stringify(pending), signal: AbortSignal.timeout(120000),
        });
        if (!["saved", "read_only"].includes(result.status) || !Number.isSafeInteger(result.snapshot?.revision) ||
            !Array.isArray(result.actions) || result.actions.some((item) => typeof item !== "string"))
          throw new Error("AI 返回的数据不完整，请重试同一请求");
        pending = null;
        try { persist(); } catch {}
        try { await refresh(result.snapshot); } catch (error) { result.refreshError = error.message; }
        return result;
      } catch (error) {
        if ([400, 409].includes(error.status)) {
          pending = null;
          try { persist(); } catch {}
        }
        throw error;
      } finally { busy = false; }
    }
    return {
      get pending() { return Boolean(pending); },
      get busy() { return busy; },
      retry: execute,
      async send(message) {
        if (busy || pending) throw new Error("先重试未确认的请求，再发送新内容");
        if (typeof message !== "string" || !message.trim() || message.length > 2000) throw new Error("请输入有效的请求");
        if (typeof window !== "undefined" && window.TravelRuntimeStorage?.hasPending())
          throw new Error("请先恢复共享记录中未确认的保存");
        busy = true;
        try {
          const current = await request(`/api/trip/${encodeURIComponent(tripId)}`, { method: "GET" });
          if (!Number.isSafeInteger(current.revision) || current.revision < 0) throw new Error("请先读取共享旅程");
          pending = { mutationId: crypto.randomUUID(), expectedRevision: current.revision, message: message.trim() };
          try { persist(); } catch { pending = null; throw new Error("浏览器无法保存恢复记录，本次未发送"); }
        } finally { busy = false; }
        return execute();
      },
    };
  }
  if (typeof module === "object" && module.exports) module.exports = { createAiController };
  if (typeof window === "undefined" || typeof document === "undefined") return;
  window.TravelAI = { createAiController };
  let initialized = false;
  function init() {
    if (initialized || !window.TRAVEL_PLAN_DATA || !document.getElementById("ai-dialog")) return;
    initialized = true;
    const $ = (id) => document.getElementById(id);
    $("ai-open").onclick = () => { $("ai-dialog").showModal(); $("ai-input").focus(); };
    $("ai-close").onclick = () => $("ai-dialog").close();
    $("ai-dialog").addEventListener("close", () => $("ai-open").focus());
    let controller;
    try {
      controller = createAiController({ tripId: window.TRAVEL_PLAN_DATA.metadata.tripId, journal: sessionStorage,
        refresh: async () => {
          await window.LightTravelRefresh?.();
          if (await window.TravelLedger?.refresh?.(true) === false) throw new Error("账本正在保存，请稍后刷新共享数据");
        } });
    } catch (error) {
      $("ai-status").textContent = error.message; $("ai-submit").disabled = true;
      $("ai-form").onsubmit = (event) => event.preventDefault();
      return;
    }
    window.TravelI18n?.addTranslations({
      "AI 旅程助手": { en: "AI travel assistant" }, "想查看或记录什么？": { en: "What would you like to check or record?" },
      "例如：添加 to-do，出发前带上雨衣": { en: "For example: add a to-do to pack a raincoat" },
      "发送": { en: "Send" }, "重试同一请求": { en: "Retry the same request" },
      "读取行程与预订；to-do、票据和账本操作按本页内容提供。行程、预订与原始附件仅供查看。不会更改商家订单。": {
        en: "Read itinerary and bookings; use the available to-do, ticket and ledger actions. Itinerary, bookings and original materials are read-only. Merchant orders are not changed.",
      },
    });
    window.TravelI18n?.apply();
    const localizePrompt = () => {
      const prompt = "例如：添加 to-do，出发前带上雨衣";
      $("ai-input").placeholder = window.TravelI18n?.text(prompt) || prompt;
    };
    localizePrompt();
    window.addEventListener("travel-language-change", localizePrompt);
    const controls = () => {
      $("ai-submit").disabled = controller.busy || controller.pending;
      $("ai-retry").hidden = !controller.pending; $("ai-retry").disabled = controller.busy;
    };
    const append = (author, message) => {
      const paragraph = document.createElement("p"); paragraph.dataset.author = author; paragraph.textContent = message;
      $("ai-conversation").append(paragraph); paragraph.scrollIntoView?.({ block: "nearest" });
    };
    async function run(action) {
      $("ai-status").textContent = "AI 正在读取和处理，请稍候…";
      const operation = action(); controls();
      try {
        const result = await operation;
        const saved = result.status === "saved" ? `已保存 ${result.actions.length} 处共享修改：\n${result.actions.join("\n")}\n\n` : "本次没有修改共享记录。\n\n";
        append("assistant", saved + (result.message || ""));
        $("ai-status").textContent = result.refreshError ? `保存结果已确认；页面刷新失败：${result.refreshError}` : "已读取最新共享记录";
        return true;
      } catch (error) {
        $("ai-status").textContent = error.message + (controller.pending ? "。保存结果未确认，请重试同一请求。" : "");
        if (error.status === 409) {
          try { await window.LightTravelRefresh?.(); await window.TravelLedger?.refresh?.(true); } catch {}
        }
        return false;
      } finally { controls(); }
    }
    $("ai-form").onsubmit = async (event) => {
      event.preventDefault(); const draft = $("ai-input").value, message = draft.trim(); if (!message) return;
      append("user", message); $("ai-input").value = "";
      const confirmed = await run(() => controller.send(message));
      if (!confirmed && !controller.pending && $("ai-input").value === "") $("ai-input").value = draft;
    };
    $("ai-retry").onclick = () => run(() => controller.retry());
    if (controller.pending) $("ai-status").textContent = "有一项请求尚未确认，请重试同一请求。";
    controls();
  }
  window.addEventListener("travel-runtime:ready", init);
  document.addEventListener("DOMContentLoaded", init);
})();
