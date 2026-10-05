import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";
const create = fileURLToPath(new URL("../create.mjs", import.meta.url));
const template = fileURLToPath(new URL("../../assets/template/", import.meta.url));
const run = (args, cwd) => spawnSync(process.execPath, args, { cwd, encoding: "utf8" });
function trip(project) {
  const file = path.join(project, "trip-data.json"), data = JSON.parse(fs.readFileSync(file));
  data.metadata.tripId = "generator-fixture"; data.metadata.title = "Fictional test";
  Object.assign(data.trip, { status: "draft", startDate: "2026-10-01", endDate: "2026-10-01", dayCount: 1 });
  data.days = [{ day: 1, date: "2026-10-01", title: "Fixture", schedule: [], locations: [] }];
  data.config.modules.itinerary = true; data.config.modules.todo = true; data.config.modules.ledger = true;
  fs.writeFileSync(file, JSON.stringify(data));
}
test("generator defaults off; enabled build adds a usable protected AI entry and retains all original modules", () => {
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "travel-ai-generator-"));
  try {
    for (const mode of ["off", "openai"]) {
      const project = path.join(temporary, mode), args = [create, project, ...(mode === "openai" ? ["--ai", mode] : [])];
      const generated = run(args); assert.equal(generated.status, 0, generated.stderr);
      assert.equal(JSON.parse(fs.readFileSync(path.join(project, "ai-config.json"))).provider, mode);
      trip(project);
      fs.writeFileSync(path.join(project, ".dev.vars"), "OPENAI_API_KEY=synthetic-private-key");
      const built = run(["scripts/build.mjs"], project); assert.equal(built.status, 0, built.stderr);
      const html = fs.readFileSync(path.join(project, "dist/index.html"), "utf8");
      assert.equal(html.includes('id="ai-open"'), mode === "openai");
      assert.equal(fs.existsSync(path.join(project, "dist/ai-ui.js")), mode === "openai");
      for (const id of ["flights", "stays", "route", "itinerary", "prep", "materials", "ledger-view", "ticket-dialog"])
        assert.ok(html.includes(`id="${id}"`), `preserve ${id}`);
      assert.ok(fs.existsSync(path.join(project, "functions/api/ai/[[tripId]].js")));
      assert.equal(fs.existsSync(path.join(project, "dist/server")), false);
      assert.equal(fs.existsSync(path.join(project, "dist/.dev.vars")), false);
      assert.equal(html.includes("synthetic-private-key"), false);
      assert.deepEqual(JSON.parse(fs.readFileSync(path.join(project, "dist/_routes.json"))).include, ["/*"]);
    }
  } finally { spawnSync("trash", [temporary]); }
});
test("invalid AI switch rejects before creating a directory; destination and credential filters remain effective", () => {
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "travel-ai-negative-"));
  try {
    const target = path.join(temporary, "invalid");
    assert.notEqual(run([create, target, "--ai", "unknown"]).status, 0); assert.equal(fs.existsSync(target), false);
    assert.notEqual(run([create, temporary]).status, 0);
    const key = "synthetic-template-credential";
    // Run from an isolated copy so no local secrets are created in the package.
    const skill = path.join(temporary, "isolated-skill");
    fs.mkdirSync(path.join(skill, "scripts"), { recursive: true }); fs.copyFileSync(create, path.join(skill, "scripts/create.mjs"));
    fs.cpSync(template, path.join(skill, "assets/template"), { recursive: true, filter: (name) => !name.split(path.sep).includes("node_modules") });
    fs.writeFileSync(path.join(skill, "assets/template/.dev.vars"), key);
    fs.writeFileSync(path.join(skill, "assets/template/.env.local"), key);
    const generated = path.join(temporary, "filtered"), result = run([path.join(skill, "scripts/create.mjs"), generated]);
    assert.equal(result.status, 0, result.stderr);
    assert.equal(fs.existsSync(path.join(generated, ".dev.vars")), false); assert.equal(fs.existsSync(path.join(generated, ".env.local")), false);
    trip(generated);
    fs.writeFileSync(path.join(generated, "ai-config.json"), JSON.stringify({ provider: "openai", OPENAI_API_KEY: key }));
    assert.notEqual(run(["scripts/build.mjs"], generated).status, 0); assert.equal(fs.existsSync(path.join(generated, "dist")), false);
  } finally { spawnSync("trash", [temporary]); }
});

test("enabled build rejects symlinked AI assets instead of publishing server credentials", () => {
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "travel-ai-symlink-"));
  try {
    for (const [index, relative] of ["ai-ui.js", "ai.css", "assets/ai-panel.html"].entries()) {
      const project = path.join(temporary, String(index));
      assert.equal(run([create, project, "--ai", "openai"]).status, 0);
      trip(project);
      const input = path.join(project, relative), secret = path.join(project, ".dev.vars");
      fs.writeFileSync(secret, "OPENAI_API_KEY=synthetic-symlink-secret");
      fs.renameSync(input, input + ".original");
      fs.symlinkSync(secret, input);
      const built = run(["scripts/build.mjs"], project);
      assert.notEqual(built.status, 0, `must reject ${relative}`);
      assert.match(built.stderr, /symlink rejected|regular file within the project/);
      assert.equal(fs.existsSync(path.join(project, "dist")), false);
    }
  } finally { spawnSync("trash", [temporary]); }
});
