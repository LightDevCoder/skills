import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { validateTrip } from "../assets/template/scripts/validate.mjs";
const [directory, input, ...extra] = process.argv.slice(2);
if (!directory || !input || extra.length)
  throw new Error(
    "Usage: node update.mjs <project-directory> <reviewed-next-trip.json>",
  );
const root = fs.realpathSync(directory),
  target = path.join(root, "trip-data.json");
if (fs.lstatSync(target).isSymbolicLink())
  throw new Error("Trip data symlink rejected");
const previous = JSON.parse(fs.readFileSync(target, "utf8")),
  next = JSON.parse(fs.readFileSync(input, "utf8"));
if (previous.metadata.tripId !== next.metadata?.tripId)
  throw new Error("Trip identity cannot change during an update");
const validation = validateTrip(next, root);
if (!validation.ok) throw new Error(validation.errors.join("\n"));
const backupDir = path.join(root, ".trip-backups");
fs.mkdirSync(backupDir, { recursive: true });
if (fs.lstatSync(backupDir).isSymbolicLink())
  throw new Error("Backup directory symlink rejected");
const backup = path.join(
  backupDir,
  `${Date.now()}-${crypto.randomUUID()}.json`,
);
fs.copyFileSync(target, backup);
fs.chmodSync(backup, 0o600);
const temporary = path.join(root, `.trip-${crypto.randomUUID()}.json`);
fs.writeFileSync(temporary, JSON.stringify(next, null, 2) + "\n", {
  mode: 0o600,
  flag: "wx",
});
fs.renameSync(temporary, target);
console.log(
  `Updated trip ${next.metadata.tripId}; previous data saved to ${backup}. Cloud runtime data was not changed.`,
);
