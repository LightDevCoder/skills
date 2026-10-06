import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { normalizeAiConfig } from "../assets/template/ai-config.js";
const args = process.argv.slice(2);
let destination, provider = "off";
for (let i = 0; i < args.length; i++) {
  if (args[i] === "--ai" && i + 1 < args.length) provider = args[++i];
  else if (!args[i].startsWith("--") && !destination) destination = args[i];
  else throw new Error("Usage: node create.mjs <new-project-directory> [--ai off|openai]");
}
if (!destination)
  throw new Error("Usage: node create.mjs <new-project-directory> [--ai off|openai]");
const ai = normalizeAiConfig({ provider });
const target = path.resolve(destination);
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
    !path.relative(template, source)
      .split(path.sep)
      .some((x) =>
        ["node_modules", ".wrangler", "dist", ".build-backups", ".trip-backups", ".dev.vars", "private", ".DS_Store"].includes(x) || x.startsWith(".env") || x.startsWith(".dist-stage-"),
      ),
});
fs.writeFileSync(path.join(target, "ai-config.json"), JSON.stringify(ai, null, 2) + "\n");
console.log(
  `Created ${target} with AI ${ai.provider}. Fill trip-data.json, npm ci, then npm run build. Cloudflare setup is described in references/deployment.md.${ai.provider === "openai" ? " Configure server OPENAI_BASE_URL, OPENAI_API_KEY and OPENAI_MODEL using references/ai-integration.md; no upstream was contacted." : ""}`,
);
