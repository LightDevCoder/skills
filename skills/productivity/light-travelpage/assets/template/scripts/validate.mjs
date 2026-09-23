import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { validTodoRecords } from "../todo-contract.js";
export function validDate(value) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value || "")) return false;
  const date = new Date(`${value}T00:00:00Z`);
  return (
    Number.isFinite(date.getTime()) && date.toISOString().slice(0, 10) === value
  );
}
const validTime = (value) => /^([01]\d|2[0-3]):[0-5]\d$/.test(value || "");
const validOffset = (value) =>
  /^[+-]\d{2}:\d{2}$/.test(value || "") &&
  Number(value.slice(4)) < 60 &&
  (Number(value.slice(1, 3)) * 60 + Number(value.slice(4))) *
    (value[0] === "-" ? -1 : 1) >=
    -720 &&
  (Number(value.slice(1, 3)) * 60 + Number(value.slice(4))) *
    (value[0] === "-" ? -1 : 1) <=
    840;
const idValid = (value) => /^[a-zA-Z0-9_-]{1,100}$/.test(value || "");
export function assetPath(root, value) {
  if (
    typeof value !== "string" ||
    !/^assets\/[A-Za-z0-9_./-]+$/.test(value) ||
    value.split("/").some((x) => x === ".." || x === "." || !x)
  )
    throw new Error("Asset must use a safe relative assets/ path");
  const base = fs.realpathSync(root),
    resolved = path.resolve(base, value);
  const stat = fs.lstatSync(resolved);
  if (
    !stat.isFile() ||
    stat.isSymbolicLink() ||
    !fs.realpathSync(resolved).startsWith(base + path.sep)
  )
    throw new Error("Asset must be a regular file within the project");
  return resolved;
}
export function validateTrip(data, root, { allowEmpty = false } = {}) {
  const errors = [],
    warnings = [];
  const check = (ok, msg) => {
    if (!ok) errors.push(msg);
  };
  if (!data || typeof data !== "object" || Array.isArray(data))
    return { ok: false, errors: ["Trip must be an object"], warnings };
  check(data.schemaVersion === "2.0-lite", "Unsupported trip schema");
  check(
    idValid(data.metadata?.tripId) && data.metadata.tripId !== "unconfigured",
    "Trip ID must be configured",
  );
  check(
    typeof data.metadata?.title === "string" && data.metadata.title.trim(),
    "Trip title required",
  );
  const modules = data.config?.modules || {},
    moduleNames = [
      "flights",
      "overview",
      "itinerary",
      "todo",
      "driving",
      "ledger",
    ];
  check(
    moduleNames.every((x) => typeof modules[x] === "boolean") &&
      Object.keys(modules).every((x) => moduleNames.includes(x) || x === "accommodations") && (modules.accommodations === undefined || typeof modules.accommodations === "boolean"),
    "Six module switches must be booleans",
  );
  check(data.config?.persistence?.mode === "d1", "Shared D1 mode is required");
  check(
    JSON.stringify(
      [...(data.config?.persistence?.sharedCollections || [])].sort(),
    ) === JSON.stringify(["ledger", "tickets", "todos"]),
    "All runtime collections must be shared",
  );
  check(
    data.config?.persistence?.apiBase === "/api/trip",
    "Use the same-origin trip API",
  );
  if (data.trip?.status === "uninitialized") {
    if (allowEmpty)
      return {
        ok:
          errors.filter((x) => x !== "Trip ID must be configured").length === 0,
        errors: errors.filter((x) => x !== "Trip ID must be configured"),
        warnings: ["Blank template, not deployable"],
      };
    errors.push("Uninitialized template cannot be deployed");
  }
  const days = Array.isArray(data.days) ? data.days : [];
  check(
    Number.isInteger(data.trip?.dayCount) &&
      data.trip.dayCount > 0 &&
      data.trip.dayCount === days.length,
    "Day count must match days",
  );
  const start = data.trip?.startDate,
    end = data.trip?.endDate;
  if (start === null && end === null && data.trip?.status === "draft")
    warnings.push("Trip dates pending");
  else {
    check(validDate(start) && validDate(end), "Invalid trip dates");
    if (validDate(start) && validDate(end))
      check(
        (Date.parse(end) - Date.parse(start)) / 86400000 + 1 === days.length,
        "Trip date span must match days",
      );
  }
  const unique = (records, label) => {
    const ids = new Set();
    if (!Array.isArray(records)) {
      errors.push(`${label} must be an array`);
      return ids;
    }
    for (const record of records) {
      check(
        idValid(record?.id) && !ids.has(record.id),
        `${label} contains missing, invalid or duplicate IDs`,
      );
      ids.add(record?.id);
    }
    return ids;
  };
  const places = unique(data.places, "places"),
    tickets = unique(data.ticketPlanning?.items, "tickets"),
    journeys = unique(data.flightJourneys, "journeys");
  const stays = unique(data.accommodations || [], "accommodations");
  const providers = ["amap", "apple", "google", "kakao", "yandex"];
  check(data.config.language === undefined || ["zh-CN", "en"].includes(data.config.language), "Unsupported default language");
  if (data.translations !== undefined) {
    check(data.translations && typeof data.translations === "object" && !Array.isArray(data.translations), "Translations must be an object");
    for (const entry of Object.values(data.translations || {})) check(entry && typeof entry === "object" && Object.keys(entry).every(k => ["en", "zh-CN"].includes(k) && typeof entry[k] === "string" && entry[k].trim().length > 0), "Invalid translation entry");
  }
  for (const place of data.places || []) {
    check(place.countryCode === undefined || /^[A-Z]{2}$/.test(place.countryCode), "Invalid place country code");
    if (place.geo) {
      check(Number.isFinite(place.geo.lat) && Math.abs(place.geo.lat) <= 90 && Number.isFinite(place.geo.lng) && Math.abs(place.geo.lng) <= 180, "Invalid place coordinates");
      check(place.geo.coordinateSystem === undefined || ["WGS84", "GCJ02", "unknown"].includes(place.geo.coordinateSystem), "Unsupported coordinate system");
      if (place.geo.coordinateSystem && place.geo.coordinateSystem !== "unknown") check(typeof place.geo.source === "string" && Boolean(place.geo.source.trim()), "Coordinate source required");
    }
    if (place.navigation?.provider) check(providers.includes(place.navigation.provider), "Unknown navigation provider");
    for (const [provider, service] of Object.entries(place.navigation?.services || {})) {
      check(providers.includes(provider) && service && typeof service === "object", "Invalid navigation service");
      if (service?.url) check(typeof service.url === "string" && service.url.startsWith("https://"), "Map URL must use HTTPS");
      if (service?.placeId) check(typeof service.placeId === "string" && /^[\w-]+$/.test(service.placeId), "Invalid map place ID");
    }
  }
  for (const stay of data.accommodations || []) {
    const status = stay.status || "pending";
    check(["pending", "confirmed", "unconfirmed"].includes(status), "Invalid accommodation status");
    for (const field of ["checkIn", "checkOut"]) check(stay[field] == null && status === "pending" || validDate(stay[field]), "Invalid accommodation date");
    if (validDate(stay.checkIn) && validDate(stay.checkOut)) check(stay.checkOut > stay.checkIn, "Accommodation checkout must follow checkin");
    for (const field of ["checkInTime", "checkOutTime"]) if(stay[field]!=null) check(validTime(stay[field]), "Invalid accommodation time");
    if(stay.placeId) check(places.has(stay.placeId), "Unknown accommodation place");
    if(status !== "pending") check(Boolean(stay.name && stay.placeId && stay.roomType), "Complete accommodation details required");
    if(stay.price) check(/^[A-Z]{3}$/.test(stay.price.currency) && Number.isFinite(stay.price.amount) && stay.price.amount>=0, "Invalid accommodation price");
    for(const id of stay.ticketIds || []) check(tickets.has(id), "Unknown accommodation ticket");
  }
  for (const journey of data.flightJourneys || []) for(const id of journey.ticketIds || []) check(tickets.has(id), "Unknown flight ticket");
  for(const id of data.demoNavigationPlaceIds || []) check(data.config.demo === true && places.has(id), "Demo navigation requires demo mode and existing place");
  unique(data.flights, "flights");
  check(validTodoRecords(data.preTrip?.packingItems), "Todo IDs, text, or completed state invalid or duplicated");
  const schedules = new Set();
  days.forEach((day, i) => {
    check(day.day === i + 1, "Days must be ordered consecutively");
    check(
      Array.isArray(day.locations) && Array.isArray(day.schedule),
      "Day locations/schedule required",
    );
    if (day.date === null && start === null)
      warnings.push(`Day ${i + 1} date pending`);
    else {
      check(validDate(day.date), `Day ${i + 1} has invalid date`);
      if (validDate(start))
        check(
          Date.parse(day.date) === Date.parse(start) + i * 86400000,
          `Day ${i + 1} date does not match trip`,
        );
    }
    for (const item of day.schedule || []) {
      check(
        idValid(item.id) && !schedules.has(item.id),
        "Schedule IDs must be unique",
      );
      schedules.add(item.id);
      if(item.accommodationId) check(stays.has(item.accommodationId), "Unknown accommodation reference");
      check(
        validTime(item.time) ||
          item.time === "待确认" ||
          item.time === "待补充",
        `Schedule ${item.id} time invalid`,
      );
      for (const id of item.ticketIds || [])
        check(tickets.has(id), `Unknown ticket ${id}`);
      for (const id of [
        ...(item.placeIds || []),
        ...(item.placeId ? [item.placeId] : []),
      ])
        check(places.has(id), `Unknown place ${id}`);
    }
  });
  for (const ticket of data.ticketPlanning?.items || []) {
    check(
      days.some((day) =>
        ticket.dayId ? day.id === ticket.dayId : day.day === ticket.day,
      ),
      `Ticket ${ticket.id} has unknown day`,
    );
    if (ticket.document) {
      check(
        ticket.document.type === "application/pdf",
        "Only PDF ticket documents supported",
      );
      try {
        const file = assetPath(root, ticket.document.url);
        check(
          file.endsWith(".pdf") &&
            fs.readFileSync(file).subarray(0, 5).toString() === "%PDF-",
          "Ticket document must be a PDF",
        );
      } catch (error) {
        errors.push(error.message);
      }
    }
  }
  for (const flight of data.flights || []) {
    check(journeys.has(flight.journeyId), "Flight references unknown journey");
    if (flight.placeholder) continue;
    for(const point of [flight.departure,flight.arrival]) if(point?.placeId) check(places.has(point.placeId), "Unknown airport place");
    for (const point of [flight.departure, flight.arrival])
      check(
        validDate(point?.date) &&
          validTime(point?.time) &&
          validOffset(point?.utcOffset),
        "Flight date/time/UTC offset invalid",
      );
    if (flight.departure && flight.arrival) {
      const iso = (p) => `${p.date}T${p.time}:00${p.utcOffset}`;
      check(
        Date.parse(iso(flight.arrival)) > Date.parse(iso(flight.departure)),
        "Flight arrival must follow departure",
      );
    }
  }
  if (modules.driving) {
    const car = data.groundTransport?.rentalCar;
    check(
      Boolean(
        car?.company &&
        car.vehicle &&
        car.price &&
        Array.isArray(data.groundTransport.rentalChecklist),
      ),
      "Rental details required",
    );
    for (const point of [car?.pickup, car?.dropoff])
      check(
        validDate(point?.date) &&
          validTime(point?.time) &&
          validOffset(point?.utcOffset),
        "Rental date/time/UTC offset invalid",
      );
    for (const point of [car?.pickup, car?.dropoff]) {
      if (point?.placeId) check((data.places || []).some(place => place.id === point.placeId), "Unknown rental placeId");
    }
    if (car?.pickup && car.dropoff)
      check(
        Date.parse(
          `${car.dropoff.date}T${car.dropoff.time}:00${car.dropoff.utcOffset}`,
        ) >
          Date.parse(
            `${car.pickup.date}T${car.pickup.time}:00${car.pickup.utcOffset}`,
          ),
        "Rental return must follow pickup",
      );
  }
  if (modules.overview) {
    const map = data.map || {},
      ids = unique(map.places, "map places");
    check(
      map.mapMode === "template-auto" && ids.size > 0,
      "Map input required",
    );
    for (const place of map.places || [])
      check(
        Number.isFinite(place.geo?.lat) &&
          Math.abs(place.geo.lat) <= 90 &&
          Number.isFinite(place.geo?.lng) &&
          Math.abs(place.geo.lng) <= 180,
        "Map coordinates invalid or pending; disable map until resolved",
      );
    for (const route of [...(map.routes || []), ...(map.dailyRoutes || [])]) {
      check(
        days.some((x) => x.day === route.day),
        "Map route references unknown day",
      );
      check(
        Array.isArray(route.placeIds) && route.placeIds.length >= 2,
        "Route requires two places",
      );
      for (const id of route.placeIds || [])
        check(ids.has(id), `Unknown map place ${id}`);
    }
    check(map.routes?.length > 0, "Map routes required");
  }
  function scan(value) {
    if (!value || typeof value !== "object") return;
    for (const [key, item] of Object.entries(value)) {
      if (
        /^(api_?key|access_?token|session_?secret|password)$/i.test(key) &&
        item
      )
        errors.push("Credential field cannot enter trip data");
      if (
        typeof item === "string" &&
        /(-----BEGIN .*PRIVATE KEY-----|AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{24,})/.test(
          item,
        )
      )
        errors.push("Credential pattern found");
      if (typeof item === "object") scan(item);
    }
  }
  scan(data);
  return { ok: errors.length === 0, errors, warnings };
}
if (
  process.argv[1] &&
  path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)
) {
  const file = path.resolve(process.argv[2] || "trip-data.json");
  try {
    const result = validateTrip(
      JSON.parse(fs.readFileSync(file, "utf8")),
      path.dirname(file),
    );
    console.log(JSON.stringify(result, null, 2));
    if (!result.ok) process.exitCode = 1;
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
