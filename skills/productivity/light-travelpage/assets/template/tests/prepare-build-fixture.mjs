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
data.ticketPlanning.items = [{ id: "ci-pdf", day: 1, name: "Fixture ticket", requirement: "Fixture", document: { url: "assets/tickets/fixture.pdf", type: "application/pdf", label: "Fixture PDF" } }];
const objects = [
  "<< /Type /Catalog /Pages 2 0 R >>",
  "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
  "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 120 120] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
  "<< /Length 36 >>\nstream\nBT /F1 12 Tf 20 60 Td (Ticket) Tj ET\nendstream",
  "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
];
let pdf = "%PDF-1.4\n";
const offsets = [0];
for (const [index, object] of objects.entries()) {
  offsets.push(Buffer.byteLength(pdf));
  pdf += `${index + 1} 0 obj\n${object}\nendobj\n`;
}
const xref = Buffer.byteLength(pdf);
pdf += `xref\n0 ${offsets.length}\n0000000000 65535 f \n`;
for (const offset of offsets.slice(1)) pdf += `${String(offset).padStart(10, "0")} 00000 n \n`;
pdf += `trailer\n<< /Size ${offsets.length} /Root 1 0 R >>\nstartxref\n${xref}\n%%EOF\n`;
fs.mkdirSync(path.join(root, "assets/tickets"), { recursive: true });
fs.writeFileSync(path.join(root, "assets/tickets/fixture.pdf"), pdf);
fs.writeFileSync(dataPath, JSON.stringify(data, null, 2) + "\n");
