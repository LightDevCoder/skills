import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";
import { validateTrip, assetPath } from "./validate.mjs";
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
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
  "app.js",
  "overview-map.js",
  "route-ui.js",
  "site-navigation.js",
  "ticket-pdf-preview.js",
  "ledger.js",
  "currencies.js",
  "runtime-storage.js",
  "sync-ui.js",
  "LICENSE",
  "trip-data.json",
];
for (const file of files) {
  const src = path.join(root, file);
  if (fs.lstatSync(src).isSymbolicLink())
    throw new Error("Runtime symlink rejected");
  fs.copyFileSync(src, path.join(stage, file));
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
