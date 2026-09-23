import fs from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const dataPath = path.join(root, "trip-data.json");
const data = JSON.parse(fs.readFileSync(dataPath, "utf8"));
data.metadata.tripId = "ci-fixture";
data.metadata.title = "CI fixture";
data.trip.status = "draft";
data.trip.startDate = "2026-10-01";
data.trip.endDate = "2026-10-01";
data.trip.dayCount = 1;
data.trip.nightCountAway = 0;
data.days = [{ day: 1, date: "2026-10-01", title: "Fixture", locations: [], schedule: [] }];
data.config.modules.itinerary = true;
data.config.modules.todo = true;
data.preTrip.packingItems = [{ id: "ci-todo", text: "Check itinerary", completed: false }];
fs.writeFileSync(dataPath, JSON.stringify(data, null, 2) + "\n");
