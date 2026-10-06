import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";
import { validateTrip, assetPath } from "./validate.mjs";
import { normalizeAiConfig } from "../ai-config.js";
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const ai = normalizeAiConfig(fs.existsSync(path.join(root, "ai-config.json"))
  ? JSON.parse(fs.readFileSync(path.join(root, "ai-config.json"), "utf8"))
  : undefined);
const data = JSON.parse(
  fs.readFileSync(path.join(root, "trip-data.json"), "utf8"),
);
const result = validateTrip(data, root);
if (!result.ok) throw new Error(result.errors.join("\n"));
const built = spawnSync(process.execPath, ["scripts/build-map.mjs"], {
  cwd: root,
  stdio: "inherit",
});
if (built.status !== 0) process.exit(built.status || 1);
const trip = JSON.parse(
  fs.readFileSync(path.join(root, "trip-data.json"), "utf8"),
);
const out = path.join(root, "dist"),
  stage = path.join(root, `.dist-stage-${crypto.randomUUID()}`);
fs.mkdirSync(stage);
const files = [
  "index.html",
  "styles.css",
  "ledger.css",
  "handbook.css",
  "app.js",
  "i18n.js",
  "map-navigation.js",
  "travel-cards.js",
  "overview-map.js",
  "route-ui.js",
  "site-navigation.js",
  "handbook.js",
  "ledger.js",
  "currencies.js",
  "runtime-storage.js",
  "sync-ui.js",
  "LICENSE",
  "trip-data.json",
];
if (ai.provider === "openai") files.push("ai-ui.js", "ai.css");
for (const file of files) {
  const src = path.join(root, file);
  if (fs.lstatSync(src).isSymbolicLink())
    throw new Error("Runtime symlink rejected");
  fs.copyFileSync(src, path.join(stage, file));
}
fs.writeFileSync(path.join(stage, "ai-config.json"), JSON.stringify(ai) + "\n");
if (ai.provider === "openai") {
  const html = fs.readFileSync(path.join(stage, "index.html"), "utf8")
    .replace("<!-- optional-ai:head -->", '<link rel="stylesheet" href="ai.css"><script src="ai-ui.js" defer></script>')
    .replace("<!-- optional-ai:body -->", fs.readFileSync(assetPath(root, "assets/ai-panel.html"), "utf8"));
  fs.writeFileSync(path.join(stage, "index.html"), html);
}
const assets = new Set([
  ...(trip.metadata.assets.routeMaps || []),
  ...(trip.ticketPlanning.items || [])
    .map((x) => x.document?.url)
    .filter(Boolean),
]);
for (const relative of assets) {
  const src = assetPath(root, relative),
    dest = path.join(stage, relative);
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.copyFileSync(src, dest);
}
for (const url of new Set((trip.ticketPlanning.items || [])
  .map((ticket) => ticket.document?.url)
  .filter((url) => typeof url === "string" && /\.pdf$/i.test(url)))) {
  const pdf = assetPath(root, url);
  const preview = path.join(stage, url.replace(/\.pdf$/i, ".png"));
  fs.mkdirSync(path.dirname(preview), { recursive: true });
  const rendered = spawnSync("pdftoppm", ["-f", "1", "-singlefile", "-r", "220", "-png", pdf, preview.slice(0, -4)], {
    cwd: root,
    stdio: "inherit",
  });
  if (rendered.error || rendered.status !== 0)
    throw new Error(`Could not render ticket preview for ${url}; pdftoppm is required`);
}
fs.writeFileSync(
  path.join(stage, "_routes.json"),
  JSON.stringify({ version: 1, include: ["/*"], exclude: [] }),
);
fs.writeFileSync(
  path.join(stage, "_headers"),
  "/*\n  Cache-Control: no-store\n  X-Content-Type-Options: nosniff\n",
);
if (fs.existsSync(out)) {
  const old = path.join(
    root,
    ".build-backups",
    new Date().toISOString().replace(/[:.]/g, "-"),
  );
  fs.mkdirSync(path.dirname(old), { recursive: true });
  fs.renameSync(out, old);
}
fs.renameSync(stage, out);
console.log(`Built protected site at ${out}`);
