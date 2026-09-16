import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
const args = process.argv.slice(2);
if (args.length !== 1)
  throw new Error("Usage: node create.mjs <new-project-directory>");
const target = path.resolve(args[0]);
if (fs.existsSync(target))
  throw new Error(
    "Destination already exists; use update.mjs for an existing trip",
  );
const template = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "../assets/template",
);
fs.cpSync(template, target, {
  recursive: true,
  filter: (source) =>
    !source
      .split(path.sep)
      .some((x) =>
        ["node_modules", ".wrangler", "dist", ".build-backups"].includes(x),
      ),
});
console.log(
  `Created ${target}. Fill trip-data.json, npm ci, then npm run build. Cloudflare setup is described in references/deployment.md.`,
);
