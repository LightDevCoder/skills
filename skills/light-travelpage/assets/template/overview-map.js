/* Golden map renderer with frozen backgrounds and deterministic trip overlays. */
const demoRouteLayers = [];
const demoPlaceLayers = [];
const MAP_ROUTE_PALETTE = ["#397dc1", "#e77e22", "#618344", "#209aaa", "#8865a5", "#df6185"];

function travelMapRegions(routeMap) {
  if (Array.isArray(routeMap?.regions) && routeMap.regions.length) {
    return routeMap.regions.filter((region) => region && region.id);
  }
  const legacy = routeMap?.demo || routeMap;
  if (!legacy || typeof legacy !== "object") return [];
  return [{
    id: legacy.id || "route-map",
    label: legacy.label || legacy.heading?.text || "路线地图",
    days: legacy.days || (legacy.routes || []).map((route) => route.day),
    ...legacy
  }];
}

function travelMapSource(routeMap, regionId) {
  const regions = travelMapRegions(routeMap);
  return regions.find((region) => region.id === regionId) || regions[0] || {};
}

function travelMapSourceForDay(routeMap, dayNumber) {
  return travelMapRegions(routeMap).find((region) =>
    region.days?.includes(dayNumber) || region.routes?.some((route) => route.day === dayNumber)
  ) || null;
}

function canonicalPlaceFor(placeId) {
  return (state.data?.places || []).find((place) => place.id === placeId) || null;
}

function projectionBoundsFor(source) {
  const raw = source?.projection?.bounds || source?.geoBounds;
  if (Array.isArray(raw) && raw.length === 4) {
    const [west, south, east, north] = raw.map(Number);
    if ([west, south, east, north].every(Number.isFinite) && east > west && north > south) {
      return { west, south, east, north };
    }
  }
  if (raw && typeof raw === "object") {
    const bounds = {
      west: Number(raw.west), south: Number(raw.south),
      east: Number(raw.east), north: Number(raw.north)
    };
    if (Object.values(bounds).every(Number.isFinite) && bounds.east > bounds.west && bounds.north > bounds.south) return bounds;
  }
  return null;
}

function projectGeoPoint(geo, source) {
  const bounds = projectionBoundsFor(source);
  const longitude = Number(geo?.lng ?? geo?.lon);
  const latitude = Number(geo?.lat);
  if (!bounds || !Number.isFinite(longitude) || !Number.isFinite(latitude)) return null;
  const canvas = source.canvas || { width: 1448, height: 1086 };
  const padding = Number(source?.projection?.padding ?? 74);
  const width = Math.max(1, canvas.width - padding * 2);
  const height = Math.max(1, canvas.height - padding * 2);
  return {
    x: padding + (longitude - bounds.west) / (bounds.east - bounds.west) * width,
    y: padding + (bounds.north - latitude) / (bounds.north - bounds.south) * height
  };
}

function normalizedMapPlace(entry, source, index) {
  const canonicalId = entry?.placeId || entry?.id;
  const canonical = canonicalPlaceFor(canonicalId);
  const projected = Number.isFinite(Number(entry?.x)) && Number.isFinite(Number(entry?.y))
    ? { x: Number(entry.x), y: Number(entry.y) }
    : projectGeoPoint(entry?.geo || canonical?.geo, source);
  if (!canonicalId || !projected) return null;
  const label = entry?.label || canonical?.nameZh || canonical?.name || canonicalId;
  const lines = Array.isArray(entry?.lines) && entry.lines.length ? entry.lines : [label];
  const defaultOffset = index % 2 ? { x: -18, y: 34, anchor: "end" } : { x: 18, y: -18, anchor: "start" };
  return {
    ...entry,
    id: canonicalId,
    placeId: canonicalId,
    x: projected.x,
    y: projected.y,
    tx: Number.isFinite(Number(entry?.tx)) ? Number(entry.tx) : projected.x + defaultOffset.x,
    ty: Number.isFinite(Number(entry?.ty)) ? Number(entry.ty) : projected.y + defaultOffset.y,
    anchor: entry?.anchor || defaultOffset.anchor,
    size: Number(entry?.size) || 24,
    color: entry?.color || MAP_ROUTE_PALETTE[index % MAP_ROUTE_PALETTE.length],
    lines,
    query: entry?.query || canonical?.navigation?.query || canonical?.googleMapsUrl || `${label}${canonical?.cityOrArea ? `, ${canonical.cityOrArea}` : ""}`,
    options: entry?.options || canonical?.navigation?.options
  };
}

function placeLayersFor(source) {
  const entries = Array.isArray(source?.places) && source.places.length
    ? source.places
    : Array.isArray(source?.placeIds)
      ? source.placeIds.map((placeId) => ({ placeId }))
      : demoPlaceLayers;
  return entries.map((entry, index) => normalizedMapPlace(entry, source, index)).filter(Boolean);
}

function routePathFromPlaces(placeIds, places, bend = 0) {
  const points = placeIds.map((placeId) => places.find((place) => place.id === placeId)).filter(Boolean);
  if (points.length < 2) return [];
  return points.slice(1).map((point, index) => {
    const previous = points[index];
    const dx = point.x - previous.x;
    const dy = point.y - previous.y;
    const normalLength = Math.max(1, Math.hypot(dx, dy));
    const curve = Number.isFinite(Number(bend)) ? Number(bend) : 0;
    const normalX = -dy / normalLength * curve;
    const normalY = dx / normalLength * curve;
    const firstX = previous.x + dx / 3 + normalX;
    const firstY = previous.y + dy / 3 + normalY;
    const secondX = previous.x + dx * 2 / 3 + normalX;
    const secondY = previous.y + dy * 2 / 3 + normalY;
    return `M${previous.x.toFixed(1)} ${previous.y.toFixed(1)} C${firstX.toFixed(1)} ${firstY.toFixed(1)} ${secondX.toFixed(1)} ${secondY.toFixed(1)} ${point.x.toFixed(1)} ${point.y.toFixed(1)}`;
  });
}

function routeLayersFor(source) {
  const routes = Array.isArray(source?.routes) && source.routes.length ? source.routes : demoRouteLayers;
  const places = placeLayersFor(source);
  return routes.map((route, index) => ({
    ...route,
    color: route.color || MAP_ROUTE_PALETTE[index % MAP_ROUTE_PALETTE.length],
    paths: Array.isArray(route.paths) && route.paths.length
      ? route.paths
      : routePathFromPlaces(route.placeIds || [], places, route.bend)
  }));
}

function travelOverviewArtwork(days, source = {}, options = {}) {
  const routeLayers = routeLayersFor(source);
  const allPlaceLayers = placeLayersFor(source);
  const overviewIds = new Set(source.overviewPlaceIds || []);
  const placeLayers = options.includeAllPlaces || !overviewIds.size
    ? allPlaceLayers
    : allPlaceLayers.filter((place) => overviewIds.has(place.id));
  const canvas = source.canvas || { width: 1448, height: 1086 };
  const heading = source.heading || { text: "DEMO MAP / 示例地图", x: 33, y: 105 };
  const legend = source.legend || { x: 35, y: 168, gap: 43 };
  const annotations = Array.isArray(source.annotations) ? source.annotations : [];
  const baseHref = source.baseImage || "assets/maps/aster-isles-base.png";
  const pathsFor = (route) => options.useDetailedRoutes || !route.overviewPaths?.length ? route.paths : route.overviewPaths;
  const esc = (value) => String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&apos;"
  })[character]);
  const multilineText = (lines, x, lineHeight = 31) => lines
    .map((line, index) => `<tspan x="${x}" dy="${index ? lineHeight : 0}">${esc(line)}</tspan>`)
    .join("");

  return `<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" viewBox="0 0 ${canvas.width} ${canvas.height}" role="img" aria-label="${esc(source.ariaLabel || "虚构示例旅行路线图")}" data-overview-version="2">
  <title>${esc(source.title || "虚构示例旅行路线")}</title>
  <desc>${esc(source.description || "原创虚构底图、旅行路线、地点标记和日期图例。")}</desc>
  <g id="overview-background" inkscape:groupmode="layer" inkscape:label="底图"><image href="${esc(baseHref)}" width="${canvas.width}" height="${canvas.height}" preserveAspectRatio="none"/></g>
  ${routeLayers.map((route) => `<g id="overview-route-${route.day}" inkscape:groupmode="layer" inkscape:label="${esc(days.find((day) => day.day === route.day)?.date || route.day)}" data-date="${esc(days.find((day) => day.day === route.day)?.date || "")}" fill="none" stroke-linecap="round" stroke-linejoin="round">${pathsFor(route).map((path) => `<path d="${esc(path)}" stroke="${esc(route.color)}" stroke-width="7"/><path d="${esc(path)}" stroke="#ffffff" stroke-opacity=".22" stroke-width="2"/>`).join("")}</g>`).join("")}
  <g id="overview-markers" inkscape:groupmode="layer" inkscape:label="地点标记">${placeLayers.map((place) => `<circle id="overview-point-${esc(place.id)}" cx="${place.x}" cy="${place.y}" r="10.5" fill="${esc(place.color)}" stroke="#fafaf4" stroke-width="2.5"/>`).join("")}</g>
  <g id="overview-place-names" inkscape:groupmode="layer" inkscape:label="地点名称" fill="#092653" stroke="#092653" stroke-width="0.4" stroke-linejoin="round" paint-order="stroke fill" font-family="'Times New Roman', 'Kaiti SC', STKaiti, KaiTi, 'Songti SC', serif" font-weight="700">${placeLayers.map((place) => `<text id="overview-label-${esc(place.id)}" x="${place.tx}" y="${place.ty}" text-anchor="${esc(place.anchor || "start")}" font-size="${place.size}">${multilineText(place.lines, place.tx)}</text>`).join("")}</g>
  <g id="overview-geographic-names" inkscape:groupmode="layer" inkscape:label="地理名称" fill="#2765a0" stroke="#2765a0" stroke-width="0.2" stroke-linejoin="round" paint-order="stroke fill" font-family="'Times New Roman',serif" font-style="italic">${annotations.map((annotation) => `<text x="${annotation.x}" y="${annotation.y}" font-size="${annotation.size || 18}" text-anchor="${esc(annotation.anchor || "start")}">${multilineText(annotation.lines || [annotation.text], annotation.x, annotation.lineHeight || 22)}</text>`).join("")}</g>
  <g id="overview-heading" inkscape:groupmode="layer" inkscape:label="标题"><text x="${heading.x}" y="${heading.y}" fill="#092653" stroke="#092653" stroke-width="0.4" stroke-linejoin="round" paint-order="stroke fill" font-size="${heading.size || 40}" font-weight="700" font-family="'Times New Roman', 'Kaiti SC', STKaiti, KaiTi, 'Songti SC', serif">${esc(heading.text)}</text></g>
  <g id="overview-date-legend" inkscape:groupmode="layer" inkscape:label="透明日期图例" font-family="'Times New Roman',serif" font-size="23" font-weight="700" fill="#092653" stroke="#092653" stroke-width="0.4" stroke-linejoin="round" paint-order="stroke fill">${routeLayers.map((route, index) => { const date = days.find((day) => day.day === route.day)?.date; if (!date) return ""; const y = legend.y + index * legend.gap; return `<g data-date="${esc(date)}"><path d="M${legend.x} ${y - 7} h28" fill="none" stroke="${esc(route.color)}" stroke-width="5" stroke-linecap="round"/><text x="${legend.x + 41}" y="${y}">${Number(date.slice(5, 7))}/${Number(date.slice(8))}</text></g>`; }).join("")}</g>
  </svg>`;
}
