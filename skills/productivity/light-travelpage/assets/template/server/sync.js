import {CURRENCY_CODES} from "../currencies.js";
import { digest, sessionValid, sameOrigin } from "./auth.js";
import { validTodoRecord, validTodoRecords } from "../todo-contract.js";
const collections = new Set([
  "todos",
  "tickets",
  "travelers",
  "bills",
  "settings",
]);
const idPattern = /^[a-zA-Z0-9_-]{1,100}$/;
export function emptyState() {
  return {
    version: 1,
    settings: null,
    bills: [],
    travelers: [],
    todos: [],
    tickets: [],
  };
}
export function validateRecord(collection, value) {
  if (!value || typeof value !== "object" || Array.isArray(value))
    throw new Error("记录必须是对象");
  if (collection !== "settings" && !idPattern.test(value.id || ""))
    throw new Error("记录 ID 无效");
  if (JSON.stringify(value).length > 20000) throw new Error("单条记录过大");
  if (collection === "todos" && !validTodoRecord(value))
    throw new Error("待办内容无效");
  if (collection === "tickets" && typeof value.completed !== "boolean")
    throw new Error("门票状态无效");
  if (
    collection === "travelers" &&
    (typeof value.name !== "string" ||
      !value.name.trim() ||
      value.name.length > 100)
  )
    throw new Error("成员名称无效");
  if (collection === "bills") {
    if (
      !Number.isSafeInteger(value.baseAmountCents) ||
      value.baseAmountCents <= 0 ||
      value.baseAmountCents > 1e12 ||
      !idPattern.test(value.payerId || "") ||
      !Array.isArray(value.participantIds) ||
      !value.participantIds.length ||
      value.participantIds.some((id) => !idPattern.test(id)) ||
      new Set(value.participantIds).size !== value.participantIds.length
    )
      throw new Error("账单金额、付款人或分摊成员无效");
    if (
      !CURRENCY_CODES.has(value.currency) ||
      !Number.isSafeInteger(value.originalAmountCents) ||
      value.originalAmountCents <= 0 ||
      value.originalAmountCents > 1e12
    )
      throw new Error("账单币种或汇率无效");
  }
  if (
    collection === "settings" &&
    (!CURRENCY_CODES.has(value.baseCurrency) ||
      !Array.isArray(value.commonCurrencies) ||
      value.commonCurrencies.some((x) => !CURRENCY_CODES.has(x)) ||
      !CURRENCY_CODES.has(value.lastCurrency))
  )
    throw new Error("账本币种设置无效");
}
export function applyChanges(snapshot, changes) {
  const next = structuredClone(snapshot);
  if (!Array.isArray(changes) || changes.length < 1 || changes.length > 1000)
    throw new Error("变更数量无效");
  const seen = new Set();
  for (const change of changes) {
    if (
      !change ||
      !collections.has(change.collection) ||
      !["upsert", "delete"].includes(change.op) ||
      !idPattern.test(change.id || "")
    )
      throw new Error("变更格式无效");
    const key = `${change.collection}:${change.id}`;
    if (seen.has(key)) throw new Error("变更包含重复记录");
    seen.add(key);
    if (change.collection === "settings") {
      if (change.id !== "settings") throw new Error("设置 ID 无效");
      if (change.op === "upsert") validateRecord("settings", change.value);
      next.settings =
        change.op === "delete" ? null : structuredClone(change.value);
      continue;
    }
    if (change.op === "upsert") {
      validateRecord(change.collection, change.value);
      if (change.id !== change.value.id) throw new Error("记录 ID 不一致");
    }
    next[change.collection] = next[change.collection].filter(
      (x) => x.id !== change.id,
    );
    if (change.op === "upsert")
      next[change.collection].push(structuredClone(change.value));
    if (next[change.collection].length > 5000)
      throw new Error("记录数量超过上限");
  }
  const travelers = new Set(next.travelers.map((x) => x.id));
  for (const bill of next.bills)
    if (
      !travelers.has(bill.payerId) ||
      bill.participantIds.some((id) => !travelers.has(id))
    )
      throw new Error("账单引用了不存在的成员");
  if (JSON.stringify(next).length > 1000000)
    throw new Error("旅程数据超过上限");
  return next;
}
const reply = (data, status = 200) =>
  Response.json(data, { status, headers: { "cache-control": "no-store" } });
async function getState(db, tripId) {
  const row = await db
    .prepare("SELECT revision, payload FROM trip_state WHERE trip_id = ?")
    .bind(tripId)
    .first();
  return row ? { ...JSON.parse(row.payload), revision: row.revision } : null;
}
export async function handleTrip(context) {
  const { env, request } = context;
  if (!(await sessionValid(request, env)))
    return reply({ error: "请重新登录旅行小组。" }, 401);
  const requestedTripId = Array.isArray(context.params.tripId) ? (context.params.tripId.length === 1 ? context.params.tripId[0] : null) : context.params.tripId;
  if (requestedTripId !== env.TRIP_ID)
    return reply({ error: "无权访问该旅程" }, 403);
  if (!env.DB) return reply({ error: "共享数据库未配置" }, 503);
  if (!["GET", "POST"].includes(request.method))
    return reply({ error: "Method not allowed" }, 405);
  if (request.method === "POST" && !sameOrigin(request))
    return reply({ error: "Forbidden" }, 403);
  const db = env.DB,
    tripId = env.TRIP_ID;
  try {
    let current = await getState(db, tripId);
    if (!current) {
      const seed = emptyState();
      const dataResponse = await env.ASSETS.fetch(
        new URL("/trip-data.json", request.url),
      );
      if (!dataResponse.ok) throw new Error("Missing seed data");
      const data = await dataResponse.json();
      if (data.metadata?.tripId !== tripId)
        throw new Error("Trip identity mismatch");
      if (!validTodoRecords(data.preTrip?.packingItems))
        throw new Error("Invalid todo seed");
      seed.todos = data.preTrip.packingItems.map((x) => ({
        id: x.id,
        text: x.text,
        completed: x.completed,
      }));
      seed.tickets = (data.ticketPlanning?.items || [])
        .filter((x) => x.purchaseStatus === "purchased")
        .map((x) => ({ id: x.id, completed: true }));
      for (const value of seed.todos) validateRecord("todos", value);
      await db
        .prepare(
          "INSERT OR IGNORE INTO trip_state (trip_id, revision, payload) VALUES (?, 0, ?)",
        )
        .bind(tripId, JSON.stringify(seed))
        .run();
      current = await getState(db, tripId);
    }
    if (request.method === "GET") return reply(current);
    if (Number(request.headers.get("content-length")) > 250000)
      return reply({ error: "请求过大" }, 413);
    const raw = await request.text();
    if (raw.length > 250000) return reply({ error: "请求过大" }, 413);
    let body;
    try {
      body = JSON.parse(raw);
    } catch {
      return reply({ error: "JSON 无效" }, 400);
    }
    if (
      !idPattern.test(body?.mutationId || "") ||
      !Number.isSafeInteger(body.expectedRevision) ||
      body.expectedRevision < 0
    )
      return reply({ error: "版本或请求标识无效" }, 400);
    const hash = await digest(raw);
    const receiptQuery = () =>
      db
        .prepare(
          "SELECT request_hash FROM mutation_receipts WHERE trip_id = ? AND mutation_id = ?",
        )
        .bind(tripId, body.mutationId)
        .first();
    const prior = await receiptQuery();
    if (prior)
      return prior.request_hash === hash
        ? reply(await getState(db, tripId))
        : reply({ error: "请求标识已用于不同内容" }, 409);
    if (current.revision !== body.expectedRevision)
      return reply(
        { error: "同行者已更新内容，请刷新后重新应用修改。", code: "conflict" },
        409,
      );
    let next;
    try {
      next = applyChanges(current, body.changes);
    } catch (error) {
      return reply({ error: error.message }, 400);
    }
    delete next.revision;
    next.updatedAt = new Date().toISOString();
    const results = await db.batch([
      db
        .prepare(
          "INSERT OR IGNORE INTO mutation_receipts (trip_id, mutation_id, request_hash, revision) SELECT ?, ?, ?, ? FROM trip_state WHERE trip_id = ? AND revision = ?",
        )
        .bind(
          tripId,
          body.mutationId,
          hash,
          current.revision + 1,
          tripId,
          current.revision,
        ),
      db
        .prepare(
          "UPDATE trip_state SET payload = ?, revision = revision + 1 WHERE trip_id = ? AND revision = ? AND EXISTS (SELECT 1 FROM mutation_receipts WHERE trip_id = ? AND mutation_id = ? AND request_hash = ? AND revision = ?)",
        )
        .bind(
          JSON.stringify(next),
          tripId,
          current.revision,
          tripId,
          body.mutationId,
          hash,
          current.revision + 1,
        ),
    ]);
    if (!results[1].meta.changes) {
      const receipt = await receiptQuery();
      if (!receipt || receipt.request_hash !== hash)
        return reply(
          {
            error: "同行者已更新内容，请刷新后重新应用修改。",
            code: "conflict",
          },
          409,
        );
    }
    return reply(await getState(db, tripId));
  } catch (error) {
    console.error("Shared state operation failed", error.name);
    return reply({ error: "共享数据暂时不可用，请稍后重试。" }, 503);
  }
}
