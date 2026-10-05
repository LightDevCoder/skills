import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { DatabaseSync } from "node:sqlite";
import vm from "node:vm";
import { Window } from "happy-dom";
import { authenticate, digest } from "../server/auth.js";
import { handleTrip } from "../server/sync.js";
import { onRequest as handleAi } from "../functions/api/ai/[[tripId]].js";
import { createOpenAiClient } from "../server/openai-client.js";

const origin = "https://example.test";
const data = () => ({ metadata: { tripId: "fixture" }, trip: { status: "draft" }, days: [], places: [],
  flights: [], flightJourneys: [], accommodations: [],
  config: { modules: { todo: true, itinerary: true, ledger: true } },
  preTrip: { packingItems: [] }, ticketPlanning: { items: [{ id: "ticket", name: "Test ticket" }] } });
function database() {
  const sqlite = new DatabaseSync(":memory:");
  for (const name of ["0001_state.sql", "0002_ai_requests.sql"])
    sqlite.exec(fs.readFileSync(new URL(`../migrations/${name}`, import.meta.url), "utf8"));
  const prepare = (sql) => ({ bind: (...values) => ({
    first: async () => sqlite.prepare(sql).get(...values) || null,
    run: async () => ({ meta: { changes: Number(sqlite.prepare(sql).run(...values).changes) } }),
  }) });
  return { prepare, close: () => sqlite.close(), batch: async (statements) => {
    sqlite.exec("BEGIN");
    try { const values = []; for (const statement of statements) values.push(await statement.run()); sqlite.exec("COMMIT"); return values; }
    catch (error) { sqlite.exec("ROLLBACK"); throw error; }
  } };
}
async function setup(t, provider = "openai", style = "chat-completions") {
  const env = { TRIP_ID: "fixture", ACCESS_CODE_HASH: await digest("synthetic-code"), SESSION_SECRET: "synthetic-session-".repeat(3),
    DB: database(), OPENAI_BASE_URL: "https://upstream.example/v1", OPENAI_API_KEY: "synthetic-server-key",
    OPENAI_MODEL: "mock-tool-model", OPENAI_API_STYLE: style,
    ASSETS: { fetch: async (url) => Response.json(new URL(url).pathname === "/ai-config.json" ? { provider } : data()) } };
  t.after(() => env.DB?.close());
  const login = await authenticate({ env, request: new Request(`${origin}/auth/login`, {
    method: "POST", headers: { origin }, body: "code=synthetic-code",
  }) });
  const cookie = login.headers.get("set-cookie").split(";")[0];
  const context = (body, options = {}) => ({ env, params: { tripId: options.tripId || "fixture" },
    request: new Request(`${origin}/api/ai/${options.tripId || "fixture"}`, {
      method: options.method || "POST", headers: { cookie, origin, ...options.headers },
      ...((options.method || "POST") === "POST" ? { body: JSON.stringify(body) } : {}),
    }) });
  const shared = () => handleTrip({ env, params: { tripId: "fixture" }, request: new Request(`${origin}/api/trip/fixture`, { headers: { cookie } }) });
  return { env, cookie, context, shared };
}
const requestBody = (mutationId = "ai-turn", message = "添加任务：带雨衣", expectedRevision = 0) => ({ mutationId, message, expectedRevision });
const tool = (name, args, id = "call-one") => ({ id, type: "function", function: { name, arguments: JSON.stringify(args) } });
const chat = (calls = [], content = "已准备好请求。") => Response.json({ choices: [{ message: { role: "assistant", content, tool_calls: calls } }] });
function mockUpstream(t, mock) {
  const original = globalThis.fetch; globalThis.fetch = mock; t.after(() => { globalThis.fetch = original; });
}

test("disabled mode does not access the upstream or D1", async (t) => {
  const s = await setup(t, "off"); const db = s.env.DB; s.env.DB = null; t.after(() => db.close());
  let upstream = 0; mockUpstream(t, async () => { upstream++; throw new Error("must not call"); });
  assert.equal((await handleAi(s.context(requestBody()))).status, 404);
  assert.equal(upstream, 0);
});
test("AI middleware and handler enforce session, trip, method and origin before upstream", async (t) => {
  const s = await setup(t); let upstream = 0; mockUpstream(t, async () => { upstream++; throw new Error("must not call"); });
  const anonymous = s.context(requestBody(), { headers: { cookie: "" } });
  assert.equal((await authenticate(anonymous)).status, 401);
  assert.equal((await handleAi(anonymous)).status, 401);
  assert.equal((await handleAi(s.context(requestBody(), { tripId: "another" }))).status, 403);
  assert.equal((await handleAi(s.context(requestBody(), { headers: { origin: "https://foreign.example" } }))).status, 403);
  assert.equal((await handleAi(s.context(undefined, { method: "GET" }))).status, 405);
  assert.equal(upstream, 0);
});
test("authenticated Chat tool mutation persists through shared API; stale and duplicate requests retain its contract", async (t) => {
  const s = await setup(t); let calls = 0;
  mockUpstream(t, async (url, options) => {
    calls++; assert.equal(url, "https://upstream.example/v1/chat/completions");
    assert.equal(options.redirect, "manual"); assert.equal(options.headers.Authorization, "Bearer synthetic-server-key");
    const body = JSON.parse(options.body); assert.equal(body.model, "mock-tool-model");
    assert.equal(options.body.includes("synthetic-server-key"), false);
    if (calls === 1) return chat([tool("create_task", { text: "带雨衣" })]);
    const output = body.messages.find((item) => item.role === "tool");
    assert.equal(output.tool_call_id, "call-one"); assert.equal(JSON.parse(output.content).status, "prepared");
    return chat([], "已准备添加雨衣任务。");
  });
  const first = await handleAi(s.context(requestBody())); assert.equal(first.status, 200);
  const saved = await first.json(); assert.equal(saved.status, "saved"); assert.equal(saved.snapshot.revision, 1);
  assert.equal(saved.snapshot.todos[0].text, "带雨衣");
  assert.equal((await (await s.shared()).json()).todos.length, 1);
  const duplicate = await handleAi(s.context(requestBody())); assert.equal(duplicate.status, 200);
  assert.equal((await duplicate.json()).snapshot.todos.length, 1); assert.equal(calls, 2);
  assert.equal((await handleAi(s.context(requestBody("ai-next", "再添加一项", 0)))).status, 409); assert.equal(calls, 2);
  assert.equal((await handleAi(s.context(requestBody("ai-turn", "different contents")))).status, 409); assert.equal(calls, 2);
});
test("Responses conversion preserves function output and encrypted continuation while keeping both out of UI", async (t) => {
  const s = await setup(t, "openai", "responses"); let calls = 0;
  mockUpstream(t, async (url, options) => {
    assert.equal(url, "https://upstream.example/v1/responses"); const body = JSON.parse(options.body);
    assert.equal(body.store, false); assert.deepEqual(body.include, ["reasoning.encrypted_content"]);
    assert.ok(body.tools.some((item) => item.type === "function" && item.name === "create_task"));
    if (++calls === 1) return Response.json({ status: "completed", output: [
      { type: "reasoning", id: "reason-1", encrypted_content: "synthetic-cipher" },
      { type: "function_call", id: "fc-1", call_id: "response-call", name: "create_task", arguments: '{"text":"检查车票"}' },
    ] });
    assert.ok(body.input.some((item) => item.type === "reasoning" && item.encrypted_content === "synthetic-cipher"));
    const output = body.input.find((item) => item.type === "function_call_output");
    assert.equal(output.call_id, "response-call"); assert.equal(JSON.parse(output.output).status, "prepared");
    return Response.json({ status: "completed", output: [{ type: "message", role: "assistant", content: [{ type: "output_text", text: "任务已准备。" }] }] });
  });
  const response = await handleAi(s.context(requestBody("response-turn"))); assert.equal(response.status, 200);
  const result = await response.json(); assert.equal(result.snapshot.todos[0].text, "检查车票");
  assert.equal(JSON.stringify(result).includes("synthetic-cipher"), false); assert.equal(Object.hasOwn(result, "responseItems"), false);
});
test("ledger tool creates referenced travelers and one integer-cent expense, then retry does not duplicate it", async (t) => {
  const s = await setup(t); let calls = 0;
  mockUpstream(t, async (_url, options) => {
    const body = JSON.parse(options.body);
    if (++calls === 1) return chat([tool("add_traveler", { name: "Alice" }, "a"), tool("add_traveler", { name: "Bob" }, "b")]);
    if (calls === 2) {
      const people = body.messages.filter((item) => item.role === "tool").map((item) => JSON.parse(item.content).record);
      return chat([tool("add_expense", { currency: "CNY", originalAmountCents: 1234,
        payerId: people[0].id, participantIds: people.map((item) => item.id), category: "餐饮", note: "午餐" })]);
    }
    return chat();
  });
  const body = requestBody("expense-turn", "添加 Alice、Bob 并记录 Alice 付的12.34元午餐，两人平分");
  const result = await (await handleAi(s.context(body))).json();
  assert.equal(result.status, "saved"); assert.equal(result.snapshot.travelers.length, 2);
  assert.equal(result.snapshot.bills[0].baseAmountCents, 1234); assert.equal(result.snapshot.bills[0].originalAmountCents, 1234);
  assert.equal((await (await handleAi(s.context(body))).json()).snapshot.bills.length, 1); assert.equal(calls, 3);
});
test("unsupported booking writes, invalid task/ticket references and missing foreign conversion save no record", async (t) => {
  const s = await setup(t); let calls = 0;
  mockUpstream(t, async () => ++calls === 1 ? chat([
    tool("update_itinerary", { text: "invented" }, "unknown"),
    tool("update_task", { id: "missing", completed: true }, "missing"),
    tool("set_ticket_status", { id: "missing", completed: true }, "ticket"),
    tool("add_expense", { currency: "JPY", originalAmountCents: 100, payerId: "missing", participantIds: ["missing"] }, "fx"),
  ]) : chat([], "这些请求无法执行。"));
  const response = await handleAi(s.context(requestBody())); assert.equal(response.status, 200);
  const result = await response.json(); assert.equal(result.status, "read_only"); assert.equal(result.snapshot.revision, 0);
  assert.equal(result.snapshot.todos.length, 0); assert.equal(result.snapshot.bills.length, 0); assert.equal(result.actions.length, 0);
});
test("upstream failure before plan completion writes nothing and never exposes its body/key", async (t) => {
  const s = await setup(t);
  mockUpstream(t, async () => new Response("upstream secret synthetic-server-key", { status: 401 }));
  const response = await handleAi(s.context(requestBody())); assert.equal(response.status, 503);
  assert.equal((await response.text()).includes("synthetic-server-key"), false);
  assert.equal((await (await s.shared()).json()).revision, 0);
});
test("transport rejects credential URLs and does not follow redirects", async () => {
  for (const baseUrl of ["https://key@example.test/v1", "https://example.test/v1?key=x", "https://example.test/v1/responses"])
    assert.throws(() => createOpenAiClient({ baseUrl }));
  const client = createOpenAiClient({ baseUrl: "https://example.test", fetchImpl: async (url, options) => {
    assert.equal(url, "https://example.test/v1/chat/completions"); assert.equal(options.redirect, "manual"); return chat();
  } });
  assert.equal((await client.complete({ model: "test", messages: [] })).role, "assistant");
  const redirect = createOpenAiClient({ baseUrl: "https://example.test/v1", fetchImpl: async (_url, options) => {
    assert.equal(options.redirect, "manual"); return new Response(null, { status: 302, headers: { location: "https://foreign.example" } });
  } });
  await assert.rejects(redirect.complete({ model: "test", messages: [] }), /HTTP 302/);
});

test("a shared edit during model processing rejects the AI plan without overwriting it", async (t) => {
  const s = await setup(t); let calls = 0;
  mockUpstream(t, async () => {
    if (++calls === 1) {
      const manual = await handleTrip({ env: s.env, params: { tripId: "fixture" }, request: new Request(`${origin}/api/trip/fixture`, {
        method: "POST", headers: { origin, cookie: s.cookie }, body: JSON.stringify({ mutationId: "manual-edit", expectedRevision: 0,
          changes: [{ collection: "todos", id: "manual", op: "upsert", value: { id: "manual", text: "同行者的更新", completed: false } }] }),
      }) });
      assert.equal(manual.status, 200); return chat([tool("create_task", { text: "AI task" })]);
    }
    return chat();
  });
  const body = requestBody("racing-ai"); assert.equal((await handleAi(s.context(body))).status, 409);
  const state = await (await s.shared()).json(); assert.equal(state.todos.length, 1); assert.equal(state.todos[0].id, "manual");
  assert.equal((await handleAi(s.context(body))).status, 409); assert.equal(calls, 2);
});

function controller(options) {
  const sandbox = { module: { exports: {} }, fetch: options.fetchImpl, crypto, AbortSignal };
  vm.runInNewContext(fs.readFileSync(new URL("../ai-ui.js", import.meta.url), "utf8"), sandbox);
  return sandbox.module.exports.createAiController(options);
}
const journal = () => { const values = new Map(); return { getItem: (key) => values.get(key) || null,
  setItem: (key, value) => values.set(key, value), removeItem: (key) => values.delete(key), values }; };
test("AI client uses only same-origin handlers, refreshes confirmed state and replays an uncertain exact body", async () => {
  const storage = journal(); let attempts = 0, exact, refreshed;
  const fetchImpl = async (url, options) => {
    assert.equal(options.credentials, "same-origin"); assert.ok(url.startsWith("/api/"));
    if (options.method === "GET") return Response.json({ revision: 0 });
    if (!exact) exact = options.body; assert.equal(options.body, exact);
    if (++attempts === 1) throw new Error("lost response");
    return Response.json({ status: "saved", actions: ["添加任务"], message: "Done", snapshot: { revision: 1, todos: [{ id: "test", text: "Raincoat", completed: false }] } });
  };
  const first = controller({ tripId: "fixture", journal: storage, fetchImpl });
  await assert.rejects(first.send("带雨衣"), /lost response/); assert.equal(first.pending, true);
  const reload = controller({ tripId: "fixture", journal: storage, fetchImpl, refresh: async (state) => { refreshed = state; } });
  assert.equal((await reload.retry()).status, "saved"); assert.equal(refreshed.todos[0].text, "Raincoat");
  assert.equal(storage.values.size, 0); assert.equal(reload.pending, false);
});
test("AI client blocks overlapping sends and clears only conclusive conflict results", async () => {
  const storage = journal(); let finishRead;
  const fetchImpl = async (_url, options) => options.method === "GET" ? await new Promise((resolve) => { finishRead = resolve; })
    : Response.json({ error: "conflict" }, { status: 409 });
  const client = controller({ tripId: "fixture", journal: storage, fetchImpl });
  const first = client.send("first"); await assert.rejects(client.send("second"), /先重试/);
  finishRead(Response.json({ revision: 0 })); await assert.rejects(first, { status: 409 });
  assert.equal(client.pending, false); assert.equal(storage.values.size, 0);
});

for (const status of [408, 429, 404]) test(`AI exact retry survives HTTP ${status} after a lost commit acknowledgement`, async () => {
  const storage = journal(), applied = new Set(), bodies = [];
  let attempts = 0;
  const fetchImpl = async (_url, options) => {
    if (options.method === "GET") return Response.json({ revision: 0 });
    bodies.push(options.body);
    if (++attempts === 2) return Response.json({ error: "Temporarily unavailable" }, { status });
    applied.add(JSON.parse(options.body).mutationId);
    if (attempts === 1) throw new Error("lost commit acknowledgement");
    return Response.json({ status: "saved", actions: ["添加费用"], snapshot: { revision: 1 } });
  };
  const first = controller({ tripId: "fixture", journal: storage, fetchImpl });
  await assert.rejects(first.send("记录合成测试费用"), /lost commit acknowledgement/);
  const persisted = [...storage.values.values()][0];
  const reload = controller({ tripId: "fixture", journal: storage, fetchImpl });
  await assert.rejects(reload.retry(), { status });
  assert.equal(reload.pending, true);
  assert.equal([...storage.values.values()][0], persisted);
  await assert.rejects(reload.send("记录合成测试费用"), /先重试/);
  assert.equal((await reload.retry()).status, "saved");
  assert.ok(bodies.every((body) => body === bodies[0]));
  assert.equal(applied.size, 1);
  assert.equal(reload.pending, false); assert.equal(storage.values.size, 0);
});
test("the shipped AI entry submits text and refreshes existing views without erasing an unrelated form draft", async () => {
  const window = new Window({ url: `${origin}/` });
  window.document.body.innerHTML = fs.readFileSync(new URL("../assets/ai-panel.html", import.meta.url), "utf8") + '<input id="unrelated-draft" value="draft remains">';
  window.TRAVEL_PLAN_DATA = { metadata: { tripId: "fixture" } }; window.AbortSignal = AbortSignal;
  let refreshed = 0, ledger = 0;
  window.LightTravelRefresh = async () => { refreshed++; };
  window.TravelLedger = { refresh: async (force) => { assert.equal(force, true); ledger++; return true; } };
  window.fetch = async (url, options) => {
    if (options.method === "GET") { assert.equal(url, "/api/trip/fixture"); return Response.json({ revision: 0 }); }
    assert.equal(url, "/api/ai/fixture"); assert.equal(JSON.parse(options.body).message, "带雨衣");
    return Response.json({ status: "saved", actions: ["添加任务：带雨衣"], message: "已准备。", snapshot: { revision: 1 } });
  };
  window.eval(fs.readFileSync(new URL("../ai-ui.js", import.meta.url), "utf8"));
  window.dispatchEvent(new window.CustomEvent("travel-runtime:ready"));
  window.document.getElementById("ai-open").click(); assert.equal(window.document.getElementById("ai-dialog").open, true);
  window.document.getElementById("ai-input").value = "带雨衣";
  window.document.getElementById("ai-form").dispatchEvent(new window.Event("submit", { cancelable: true, bubbles: true }));
  for (let retry = 0; retry < 50 && !window.document.querySelector('[data-author="assistant"]'); retry++) await new Promise((resolve) => setTimeout(resolve, 2));
  assert.match(window.document.querySelector('[data-author="assistant"]').textContent, /已保存 1 处共享修改/);
  assert.equal(refreshed, 1); assert.equal(ledger, 1); assert.equal(window.document.getElementById("unrelated-draft").value, "draft remains");
  window.document.getElementById("ai-close").click(); assert.equal(window.document.getElementById("ai-dialog").open, false);
  await window.happyDOM.abort();
});

test("AI keeps an unsent draft after a failed shared-state read and allows submitting it again", async (t) => {
  const window = new Window({ url: `${origin}/` });
  t.after(() => window.happyDOM.abort());
  window.document.body.innerHTML = fs.readFileSync(new URL("../assets/ai-panel.html", import.meta.url), "utf8");
  window.TRAVEL_PLAN_DATA = { metadata: { tripId: "fixture" } }; window.AbortSignal = AbortSignal;
  let reads = 0, writes = 0;
  window.fetch = async (_url, options) => {
    if (options.method === "GET") {
      if (++reads === 1) throw new Error("shared state offline");
      return Response.json({ revision: 0 });
    }
    writes++;
    assert.equal(JSON.parse(options.body).message, "带上雨衣");
    return Response.json({ status: "saved", actions: ["添加 to-do"], snapshot: { revision: 1 } });
  };
  window.eval(fs.readFileSync(new URL("../ai-ui.js", import.meta.url), "utf8"));
  window.dispatchEvent(new window.CustomEvent("travel-runtime:ready"));
  const input = window.document.getElementById("ai-input"), form = window.document.getElementById("ai-form");
  input.value = "  带上雨衣  ";
  await form.onsubmit({ preventDefault() {} });
  assert.equal(writes, 0);
  assert.equal(input.value, "  带上雨衣  ");
  assert.equal(window.document.getElementById("ai-retry").hidden, true);
  assert.equal(window.document.getElementById("ai-submit").disabled, false);
  await form.onsubmit({ preventDefault() {} });
  assert.equal(writes, 1);
  assert.equal(input.value, "");
});

test("AI storage initialization failure remains visible in an operable dialog without sending", async (t) => {
  const window = new Window({ url: `${origin}/` });
  t.after(() => window.happyDOM.abort());
  window.document.body.innerHTML = fs.readFileSync(new URL("../assets/ai-panel.html", import.meta.url), "utf8");
  window.TRAVEL_PLAN_DATA = { metadata: { tripId: "fixture" } };
  window.eval('Object.defineProperty(globalThis, "sessionStorage", { get() { throw new Error("storage unavailable"); } })');
  window.fetch = async () => { assert.fail("initialization failure must not send a request"); };
  window.eval(fs.readFileSync(new URL("../ai-ui.js", import.meta.url), "utf8"));
  window.dispatchEvent(new window.CustomEvent("travel-runtime:ready"));
  window.document.getElementById("ai-open").click();
  assert.equal(window.document.getElementById("ai-dialog").open, true);
  assert.ok(window.document.getElementById("ai-status").textContent.trim(), "storage failure must be visible");
  assert.equal(window.document.getElementById("ai-submit").disabled, true);
  window.document.getElementById("ai-close").click();
  assert.equal(window.document.getElementById("ai-dialog").open, false);
});

test("a failed AI preflight preserves a newer draft typed while waiting", async (t) => {
  const window = new Window({ url: `${origin}/` });
  t.after(() => window.happyDOM.abort());
  window.document.body.innerHTML = fs.readFileSync(new URL("../assets/ai-panel.html", import.meta.url), "utf8");
  window.TRAVEL_PLAN_DATA = { metadata: { tripId: "fixture" } };
  let failRead;
  window.fetch = async () => new Promise((_resolve, reject) => { failRead = reject; });
  window.eval(fs.readFileSync(new URL("../ai-ui.js", import.meta.url), "utf8"));
  window.dispatchEvent(new window.CustomEvent("travel-runtime:ready"));
  const input = window.document.getElementById("ai-input");
  input.value = "旧请求";
  const operation = window.document.getElementById("ai-form").onsubmit({ preventDefault() {} });
  input.value = "正在写的新请求";
  failRead(new Error("offline"));
  await operation;
  assert.equal(input.value, "正在写的新请求");
});

test("uncertain AI submission keeps its retry path instead of restoring a duplicate-send draft", async (t) => {
  const window = new Window({ url: `${origin}/` });
  t.after(() => window.happyDOM.abort());
  window.document.body.innerHTML = fs.readFileSync(new URL("../assets/ai-panel.html", import.meta.url), "utf8");
  window.TRAVEL_PLAN_DATA = { metadata: { tripId: "fixture" } }; window.AbortSignal = AbortSignal;
  let sends = 0;
  window.fetch = async (_url, options) => {
    if (options.method === "GET") return Response.json({ revision: 0 });
    sends++; throw new Error("lost acknowledgement");
  };
  window.eval(fs.readFileSync(new URL("../ai-ui.js", import.meta.url), "utf8"));
  window.dispatchEvent(new window.CustomEvent("travel-runtime:ready"));
  window.document.getElementById("ai-input").value = "带雨衣";
  await window.document.getElementById("ai-form").onsubmit({ preventDefault() {} });
  assert.equal(sends, 1);
  assert.equal(window.document.getElementById("ai-input").value, "");
  assert.equal(window.document.getElementById("ai-submit").disabled, true);
  assert.equal(window.document.getElementById("ai-retry").hidden, false);
  assert.ok(window.sessionStorage.getItem("light-ai-pending:fixture"));
});
