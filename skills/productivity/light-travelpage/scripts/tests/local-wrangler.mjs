// Synthetic-only local Functions + D1 integration. No remote resources or CPA.
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import http from "node:http";
import { spawn, spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { digest } from "../../assets/template/server/auth.js";

const template = fileURLToPath(new URL("../../assets/template/", import.meta.url));
const create = fileURLToPath(new URL("../create.mjs", import.meta.url));
const wrangler = path.join(template, "node_modules/wrangler/bin/wrangler.js");
const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "travel-ai-wrangler-"));
let processWorker, calls = 0;
const upstream = http.createServer(async (request, response) => {
  let raw = ""; for await (const chunk of request) raw += chunk;
  const body = JSON.parse(raw); assert.equal(request.url, "/v1/chat/completions");
  assert.equal(request.headers.authorization, "Bearer synthetic-upstream-key");
  calls++;
  response.setHeader("content-type", "application/json");
  response.end(JSON.stringify({ choices: [{ message: { role: "assistant", content: "准备添加本地测试任务。",
    tool_calls: body.messages.some((item) => item.role === "tool") ? [] : [{ id: "local-call", type: "function",
      function: { name: "create_task", arguments: '{"text":"本地链路检查"}' } }],
  } }] }));
});
const command = (args, cwd) => {
  const result = spawnSync(process.execPath, args, { cwd, encoding: "utf8", timeout: 60000, env: { ...process.env,
    WRANGLER_SEND_METRICS: "false", XDG_CONFIG_HOME: path.join(temporary, "config"), WRANGLER_LOG_PATH: path.join(temporary, "wrangler.log") } });
  assert.equal(result.status, 0, result.stderr + result.stdout); return result;
};
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
try {
  await new Promise((resolve, reject) => { upstream.once("error", reject); upstream.listen(0, "127.0.0.1", resolve); });
  const project = path.join(temporary, "site"); command([create, project, "--ai", "openai"]);
  const file = path.join(project, "trip-data.json"), data = JSON.parse(fs.readFileSync(file));
  data.metadata.tripId = "local-ai-fixture"; data.metadata.title = "Synthetic local integration";
  Object.assign(data.trip, { status: "draft", startDate: "2026-10-01", endDate: "2026-10-01", dayCount: 1 });
  data.days = [{ day: 1, date: "2026-10-01", title: "Fixture", locations: [], schedule: [] }];
  data.config.modules.itinerary = true; data.config.modules.todo = true; data.config.modules.ledger = true;
  fs.writeFileSync(file, JSON.stringify(data));
  const settings = { name: "local-ai-fixture", compatibility_date: "2026-09-11", pages_build_output_dir: "./dist",
    vars: { TRIP_ID: data.metadata.tripId },
    d1_databases: [{ binding: "DB", database_name: "local-ai-fixture", database_id: "00000000-0000-0000-0000-000000000001", migrations_dir: "migrations" }] };
  fs.writeFileSync(path.join(project, "wrangler.jsonc"), JSON.stringify(settings));
  const secrets = `ACCESS_CODE_HASH=${await digest("synthetic-local-code")}\nSESSION_SECRET=${"synthetic-local-session-".repeat(3)}\nOPENAI_BASE_URL=http://127.0.0.1:${upstream.address().port}/v1\nOPENAI_API_KEY=synthetic-upstream-key\nOPENAI_MODEL=synthetic-tool-model\n`;
  fs.writeFileSync(path.join(project, ".dev.vars"), secrets, { mode: 0o600 });
  command(["scripts/build.mjs"], project);
  command([wrangler, "d1", "migrations", "apply", "local-ai-fixture", "--local"], project);
  const probe = http.createServer(); await new Promise((resolve) => probe.listen(0, "127.0.0.1", resolve));
  const port = probe.address().port; await new Promise((resolve) => probe.close(resolve));
  let workerLogs = "";
  processWorker = spawn(process.execPath, [wrangler, "pages", "dev", "dist", "--port", String(port), "--ip", "127.0.0.1"], {
    cwd: project, env: { ...process.env, WRANGLER_SEND_METRICS: "false", XDG_CONFIG_HOME: path.join(temporary, "config"), WRANGLER_LOG_PATH: path.join(temporary, "wrangler.log") },
    stdio: ["ignore", "pipe", "pipe"],
  });
  processWorker.stdout.on("data", (chunk) => { workerLogs += chunk; });
  processWorker.stderr.on("data", (chunk) => { workerLogs += chunk; });
  const origin = `http://127.0.0.1:${port}`;
  let ready = false;
  for (let retry = 0; retry < 100; retry++) {
    if (processWorker.exitCode !== null) throw new Error(workerLogs);
    try { if ((await fetch(`${origin}/login`)).ok) { ready = true; break; } } catch {}
    await wait(100);
  }
  assert.equal(ready, true, workerLogs);
  const anonymous = await fetch(`${origin}/api/ai/local-ai-fixture`, { method: "POST", headers: { origin }, body: "{}" });
  assert.equal(anonymous.status, 401); assert.equal(calls, 0);
  const login = await fetch(`${origin}/auth/login`, { method: "POST", headers: { origin }, body: "code=synthetic-local-code", redirect: "manual" });
  assert.equal(login.status, 303); const cookie = login.headers.get("set-cookie").split(";")[0];
  const page = await fetch(origin, { headers: { cookie } }); assert.equal(page.status, 200); assert.ok((await page.text()).includes('id="ai-open"'));
  const body = JSON.stringify({ mutationId: "local-smoke", expectedRevision: 0, message: "添加任务：本地链路检查" });
  const send = (json = body, headers = {}) => fetch(`${origin}/api/ai/local-ai-fixture`, {
    method: "POST", headers: { origin, cookie, "content-type": "application/json", ...headers }, body: json,
  });
  assert.equal((await send(body, { origin: "https://foreign.example" })).status, 403);
  assert.equal((await fetch(`${origin}/api/ai/another`, { method: "POST", headers: { origin, cookie }, body })).status, 403);
  const saved = await send();
  if (saved.status !== 200) await wait(200);
  assert.equal(saved.status, 200, `${await saved.clone().text()}\n${workerLogs}\nupstream requests: ${calls}`);
  const result = await saved.json(); assert.equal(result.status, "saved"); assert.equal(result.snapshot.todos[0].text, "本地链路检查");
  assert.equal(calls, 2);
  const read = await fetch(`${origin}/api/trip/local-ai-fixture`, { headers: { cookie } }); assert.equal((await read.json()).todos.length, 1);
  assert.equal((await send()).status, 200); assert.equal(calls, 2);
  assert.equal((await send(JSON.stringify({ mutationId: "stale-smoke", expectedRevision: 0, message: "another task" }))).status, 409); assert.equal(calls, 2);
  fs.writeFileSync(path.join(project, "dist/ai-config.json"), '{"provider":"off"}');
  assert.equal((await send()).status, 404); assert.equal(calls, 2);
  console.log("Local Wrangler Functions + D1: auth, real tool mutation, shared refresh, duplicate retry, stale revision and disabled no-upstream passed. Upstream was synthetic; no remote resource was used.");
} finally {
  if (processWorker && processWorker.exitCode === null) {
    const exited = new Promise((resolve) => processWorker.once("exit", resolve));
    processWorker.kill("SIGTERM"); await Promise.race([exited, wait(3000)]);
    if (processWorker.exitCode === null) processWorker.kill("SIGKILL");
  }
  await new Promise((resolve) => upstream.close(resolve));
  spawnSync("trash", [temporary]);
}
