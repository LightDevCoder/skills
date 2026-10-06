/* Golden route interaction reused with frozen map templates. */
let mapRoutes = [];
let mapInstance = 0;
const transportNames = {
  drive: "自驾", train: "火车", rail: "火车", "cable-car": "缆车",
  hike: "步行", walk: "步行", return: "返程", "rental-car": "租车",
  boat: "游船", ferry: "渡轮", flight: "飞行", transfer: "接驳"
};

function mapRouteDefinitions(source) {
  return routeLayersFor(source).map(({ day, color }) => ({ day, color }));
}

function dailyMapLayoutFor(source, dayNumber) {
  const authored = source.dailyLayouts?.[String(dayNumber)];
  if (authored) return { places: [], labels: {}, transport: [], ...authored };
  const route = routeLayersFor(source).find((candidate) => candidate.day === dayNumber);
  if (!route) return null;
  return { places: route.placeIds || [], labels: {}, transport: [] };
}

function placeOptions(source, placeId) {
  const place = placeLayersFor(source).find((item) => item.id === placeId);
  if (!place) return [[placeId, placeId]];
  if (Array.isArray(place.options) && place.options.length) return place.options.map((option) => [option.label, option.query]);
  return [[place.lines?.at(-1) || placeId, place.query || place.lines?.[0] || placeId]];
}

function scheduleItemsForPin(day, pin) {
  const references = Array.isArray(pin?.itemIds) && pin.itemIds.length ? pin.itemIds : pin?.items || [];
  return references.map((reference) => typeof reference === "number"
    ? day.schedule[reference]
    : day.schedule.find((item) => item.id === reference)
  ).filter(Boolean);
}

function dailyViewportFor(source) {
  const canvas = source.canvas || { width: 1448, height: 1086 };
  return { x: 0, y: 0, width: canvas.width, height: canvas.height };
}

function transportIcon(type) {
  const icons = {
    drive: '<path d="m5 9 2-5h10l2 5M4 9h16v9H4zM7 18v2m10-2v2M7 12h1m8 0h1"/>',
    "cable-car": '<path d="m2 4 20-2M12 3v5M6 9h12l2 9H4zM6 18v3h12v-3M9 9v9m6-9v9"/>',
    train: '<rect x="5" y="3" width="14" height="15" rx="3"/><path d="M5 10h14M12 3v7m-4 5h1m6 0h1M8 18l-3 4m11-4 3 4M7 20h10"/>',
    hike: '<circle cx="14" cy="4" r="2"/><path d="m11 8 4 2 3 4m-7-6-3 6-4 1m7-3 3 4-1 6m-2-10-3 7-4 3M8 8l-2 3"/>',
    boat: '<path d="M12 3v11M5 7h14v6M3 14l9-3 9 3-3 6H6zM2 22q3-3 5 0 3-3 5 0 3-3 5 0 3-3 5 0"/>',
    "rental-car": '<path d="m3 10 2-5h9l2 5M2 10h15v8H2zM5 18v2m9-2v2M5 13h1m7 0h1M18 4h4m-2-2 2 2-2 2"/>',
    flight: '<path d="M3 16 21 8M9 13 5 6l2-1 6 5m2-1 1-6 2-1 1 5M8 15l-1 4 2-1 3-4"/>'
  };
  const key = type === "rail" ? "train" : type === "ferry" ? "boat" : type === "walk" ? "hike" : ["return", "transfer"].includes(type) ? "drive" : type;
  return `<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">${icons[key] || icons.drive}</svg>`;
}

function mapArtwork(source, selected, id, viewport) {
  if (!selected) return travelOverviewArtwork(state.data.days, source);
  const layout = dailyMapLayoutFor(source, selected.day);
  const day = state.data.days.find((item) => item.day === selected.day);
  const doc = new DOMParser().parseFromString(travelOverviewArtwork(state.data.days, source, { includeAllPlaces: true, useDetailedRoutes: true }), "image/svg+xml");
  const svg = doc.documentElement;
  svg.removeAttribute("data-overview-version");
  svg.setAttribute("data-daily-version", "3");
  svg.setAttribute("aria-label", day.title);
  svg.querySelector("title").textContent = day.title;
  svg.querySelector("desc").textContent = "仅显示当天路线；地点圆点打开地图，交通图标查看行程。";
  svg.querySelectorAll('[id^="overview-route-"]').forEach((group) => {
    if (group.id !== `overview-route-${selected.day}`) group.remove();
  });
  ["overview-date-legend", "overview-markers", "overview-geographic-names"].forEach((key) => svg.querySelector(`#${key}`)?.remove());
  svg.querySelectorAll('[id^="overview-label-"]').forEach((label) => {
    const placeId = label.id.replace("overview-label-", "");
    if (!layout?.places.includes(placeId)) { label.remove(); svg.querySelector(`#map-leader-${placeId}`)?.remove(); return; }
    const place = placeLayersFor(source).find((item) => item.id === placeId);
    const labelLayout = layout.labels?.[placeId] || { x: place?.tx, y: place?.ty, anchor: place?.anchor };
    if (!Number.isFinite(Number(labelLayout.x)) || !Number.isFinite(Number(labelLayout.y))) { label.remove(); return; }
    label.setAttribute("x", labelLayout.x);
    label.setAttribute("y", labelLayout.y);
    label.setAttribute("text-anchor", labelLayout.anchor || "start");
    label.querySelectorAll("tspan").forEach((line) => line.setAttribute("x", labelLayout.x));
  });
  svg.querySelectorAll("[id]").forEach((element) => { element.id = `${id}-${element.id}`; });
  return new XMLSerializer().serializeToString(svg);
}

function dailyPointRole(layout, placeId, index) {
  if (layout.roles?.[placeId]) return layout.roles[placeId];
  if (layout.places.length === 1) return "起点 / 终点";
  if (index === 0) return "起点";
  if (index === layout.places.length - 1) return "终点";
  return "途经点";
}

function travelMapMarkup(source, route) {
  const id = `travel-map-${++mapInstance}`;
  const day = route && state.data.days.find((item) => item.day === route.day);
  const layout = route && dailyMapLayoutFor(source, route.day);
  const canvas = source.canvas || { width: 1448, height: 1086 };
  const viewport = route ? dailyViewportFor(source, layout) : { x: 0, y: 0, width: canvas.width, height: canvas.height };
  const position = (x, y) => `left:${(x - viewport.x) / viewport.width * 100}%;top:${(y - viewport.y) / viewport.height * 100}%`;
  const placeLayers = placeLayersFor(source);
  const places = route && layout ? layout.places.map((placeId, index) => {
    const place = placeLayers.find((item) => item.id === placeId);
    if (!place) return "";
    const role = dailyPointRole(layout, placeId, index);
    return `<button type="button" class="map-place-dot" style="${position(place.x, place.y)}" data-map-region="${escapeHtml(source.id)}" data-place-id="${placeId}" data-place-day="${day.day}" data-place-role="${role}" aria-label="${role}：${escapeHtml(placeOptions(source, placeId)[0][0])}，打开 Google Maps" aria-haspopup="dialog" aria-expanded="false"><span></span></button>`;
  }).join("") : "";
  const transport = route && layout ? layout.transport.map((pin, index) => {
    const item = scheduleItemsForPin(day, pin)[0];
    if (!item) return "";
    return `<button class="transport-pin" type="button" style="${position(pin.x, pin.y)}" data-map-region="${escapeHtml(source.id)}" data-transport-day="${day.day}" data-transport-group="${index}" aria-expanded="false" aria-haspopup="dialog" aria-label="查看${escapeHtml(transportNames[item.type] || "交通")}：${escapeHtml(item.text)}">${transportIcon(item.type)}</button>`;
  }).join("") : "";
  const mapNote = source.disclaimer || "本图为模板化行程示意图，仅表达地点的相对方位与路线顺序，不代表真实比例或精确地理边界。如需使用真实国家或城市地图，可在生成后自行调整。";
  return `<div class="travel-map-block ${route ? "is-daily" : "is-overview"}" data-map-mode="${escapeHtml(source.mapMode || "")}" ${route ? `style="--route-color:${route.color}"` : ""}>
    <div class="travel-map-scroll"><div class="travel-map-canvas" id="${id}">${mapArtwork(source, route, id, viewport)}${places}${transport}</div></div>
    <div class="map-utility"><span>${route ? "点圆点看地图 · 点图标看交通" : escapeHtml(mapNote)}</span><button type="button" data-expand-map="${id}">放大 ↗</button></div>
  </div>`;
}

function mapZoomScrollLeft(region, canvasWidth, viewportWidth, geographicOverview) {
  const centered = Math.max(0, (canvasWidth - viewportWidth) / 2);
  const frame = region?.projection?.frame;
  if (!geographicOverview || !frame || !Number.isFinite(frame.x) || !Number.isFinite(frame.width)) return centered;
  return Math.max(0, (frame.x + frame.width / 2) / (region.canvas?.width || 1448) * canvasWidth - viewportWidth / 2);
}

function activateDayMaps(root) {
  $$(".is-daily .travel-map-scroll", root).forEach((view) => {
    if (view.dataset.positioned || !view.clientWidth) return;
    view.scrollLeft = 0;
    view.dataset.positioned = "true";
  });
}

function renderRoutePanel(regionId, dayNumber = 0) {
  const root = $("#route-explorer");
  const routeMap = state.data?.routeMap;
  const regions = travelMapRegions(routeMap);
  const source = travelMapSource(routeMap, regionId || routeMap?.defaultRegionId || root.dataset.region);
  root.dataset.region = source.id || "";
  mapRoutes = mapRouteDefinitions(source);
  const route = mapRoutes.find((item) => item.day === dayNumber);
  root.innerHTML = `<div class="route-region-tabs" aria-label="旅行国家">${regions.map((region) => `<button type="button" data-route-region="${escapeHtml(region.id)}" aria-pressed="${region.id === source.id}">${escapeHtml(region.label || region.heading?.text || region.id)}</button>`).join("")}</div>
  <div class="route-day-tabs" aria-label="${escapeHtml(source.label || "当前国家")}路线日期"><button type="button" data-route-day="0" aria-pressed="${!route}">总览</button>${mapRoutes.map((item) => { const day = state.data.days.find((candidate) => candidate.day === item.day); return day ? `<button type="button" data-route-day="${item.day}" style="--route-color:${item.color}" aria-pressed="${item === route}"><i></i>${escapeHtml(day.date ? day.date.slice(5).replace("-", "/") : `DAY ${day.day}`)}</button>` : ""; }).join("")}</div>${travelMapMarkup(source, route)}`;
  if (route) activateDayMaps(root);
}

function setupRouteExplorer() {
  renderRoutePanel();
  setupHandbookMaps();
  let activePin = null;
  let popover = null;
  const closePopover = (restoreFocus = false) => {
    const opener = activePin;
    if (opener) { opener.setAttribute("aria-expanded", "false"); opener.removeAttribute("aria-controls"); }
    popover?.remove(); popover = null; activePin = null;
    if (restoreFocus) opener?.focus({ preventScroll: true });
  };
  const positionPopover = () => {
    if (!popover || !activePin) return;
    const point = activePin.getBoundingClientRect();
    popover.style.left = `${Math.max(8, Math.min(innerWidth - popover.offsetWidth - 8, point.left + point.width / 2 - popover.offsetWidth / 2))}px`;
    popover.style.top = `${Math.max(8, Math.min(innerHeight - popover.offsetHeight - 8, point.top - popover.offsetHeight - 10))}px`;
  };
  const showPopover = (pin, content, map = false) => {
    const wasOpen = activePin === pin; closePopover(); if (wasOpen) return;
    activePin = pin; pin.setAttribute("aria-expanded", "true"); pin.setAttribute("aria-controls", "route-active-popover");
    popover = document.createElement("section"); popover.id = "route-active-popover"; popover.className = `route-popover ${map ? "route-place-popover" : "transport-popover"}`;
    popover.setAttribute("role", "dialog"); popover.setAttribute("aria-label", map ? "地点 Google Maps" : "交通信息");
    popover.innerHTML = `<button type="button" class="route-popover-close" data-close-route-popover aria-label="关闭">×</button>${content}`;
    (pin.closest("dialog") || document.body).append(popover); positionPopover();
    popover.querySelector("[data-close-route-popover]").focus({ preventScroll: true });
  };
  document.addEventListener("click", (event) => {
    const region = event.target.closest("[data-route-region]");
    const dayButton = event.target.closest("[data-route-day]");
    if (region || dayButton) {
      closePopover();
      const selectedRegionId = region?.dataset.routeRegion || $("#route-explorer").dataset.region;
      renderRoutePanel(selectedRegionId, region ? 0 : Number(dayButton?.dataset.routeDay || 0));
      return;
    }
    if (event.target.closest("[data-close-route-popover]")) { closePopover(true); return; }
    const placePin = event.target.closest("[data-place-id]");
    if (placePin) {
      const place = state.data.places.find(p => p.id === placePin.dataset.placeId);
      if (place) { closePopover(); window.TravelMaps.open(place, placePin); }
      return;
    }
    const pin = event.target.closest("[data-transport-day]");
    if (pin) {
      const day = state.data.days.find((item) => item.day === Number(pin.dataset.transportDay));
      const source = travelMapSource(state.data?.routeMap, pin.dataset.mapRegion);
      const group = dailyMapLayoutFor(source, day.day).transport[Number(pin.dataset.transportGroup)];
      showPopover(pin, scheduleItemsForPin(day, group).map((item) => `<div class="transport-leg"><strong>${escapeHtml(transportNames[item.type] || "交通")} · ${escapeHtml(item.time)}</strong><p>${escapeHtml(item.text)}</p></div>`).join(""));
      return;
    }
    if (event.target.closest(".route-popover")) return;
    closePopover();
    const zoom = event.target.closest("[data-expand-map]");
    if (zoom) {
      const dialog = $("#map-dialog");
      const source = document.getElementById(zoom.dataset.expandMap);
      const copy = source.cloneNode(true);
      const svg = copy.querySelector("svg");
      const ids = [...svg.querySelectorAll("[id]")].map((element) => element.id);
      for (const oldId of ids) svg.innerHTML = svg.innerHTML.replaceAll(`id="${oldId}"`, `id="${oldId}-zoom"`).replaceAll(`url(#${oldId})`, `url(#${oldId}-zoom)`);
      copy.removeAttribute("id"); copy.classList.toggle("daily-fullscreen", Boolean(source.closest(".is-daily")));
      copy.style.setProperty("--route-color", getComputedStyle(source).getPropertyValue("--route-color"));
      $("#map-dialog-content").replaceChildren(copy); dialog.showModal();
      const viewport = $("#map-dialog-content");
      const region = travelMapSource(state.data?.routeMap, $("#route-explorer").dataset.region);
      viewport.scrollLeft = mapZoomScrollLeft(region, copy.scrollWidth, viewport.clientWidth,
        Boolean(source.closest('.is-overview[data-map-mode="geographic-inset"]')));
    }
    const link = event.target.closest("[data-open-day]");
    if (link) {
      event.preventDefault();
      const button = $(`[data-day="${Number(link.dataset.openDay)}"] .day-toggle`);
      if (button.getAttribute("aria-expanded") !== "true") button.click();
      button.scrollIntoView({ behavior: "smooth" });
    }
    const toggle = event.target.closest(".day-toggle");
    if (toggle && toggle.getAttribute("aria-expanded") === "true") activateDayMaps(toggle.closest(".day-card"));
  });
  document.addEventListener("keydown", (event) => { if (event.key === "Escape" && activePin) { event.preventDefault(); event.stopPropagation(); closePopover(true); } });
  window.addEventListener("resize", positionPopover);
  document.addEventListener("scroll", (event) => { if (!event.target.closest?.(".route-popover")) positionPopover(); }, true);
  document.addEventListener("focusin", (event) => { if (popover && !popover.contains(event.target) && event.target !== activePin) closePopover(); });
  window.addEventListener("travel-view:shown", () => {
    const roots = [$("#route-explorer"), ...$$(".day-detail:not([hidden])")].filter(Boolean);
    roots.forEach((root) => {
      $$(".is-daily .travel-map-scroll", root).forEach((view) => view.removeAttribute("data-positioned"));
      activateDayMaps(root);
    });
  });
  $("#map-close").onclick = () => $("#map-dialog").close();
  $("#map-dialog").addEventListener("close", () => closePopover());
  $$(".day-detail:not([hidden])").forEach(activateDayMaps);
}

// Each daily map reads the same supplied schedule as its adjacent itinerary.
const handbookMapSelections = new Map();

function handbookSchedulePlaces(item) {
  const ids = schedulePlaceIds(item);
  return ids.length ? ids.map(id => {
    const place = canonicalPlaceFor(id);
    return { id, label:place?.nameZh || place?.name || id };
  }) : navigationDestinations(item);
}

function handbookRoutePoints(day, source) {
  const bounds = projectionBoundsFor(source);
  const frame = source.projection?.frame;
  const layers = placeLayersFor(source);
  const result = [];
  const seen = new Set();
  for (const item of day.schedule) {
    for (const destination of handbookSchedulePlaces(item)) {
      const place = canonicalPlaceFor(destination.id);
      const layer = layers.find(entry => entry.id === destination.id);
      let xy = layer ? [layer.x, layer.y] : null;
      const geo = place?.geo;
      if (bounds && frame && geo) {
        const lng = Number(geo.lng), lat = Number(geo.lat);
        if (!Number.isFinite(lng) || !Number.isFinite(lat) || lng < bounds.west || lng > bounds.east || lat < bounds.south || lat > bounds.north) continue;
        const cosine = Math.cos((bounds.south + bounds.north) / 2 * Math.PI / 180);
        const scale = Math.min(frame.width / ((bounds.east - bounds.west) * cosine), frame.height / (bounds.north - bounds.south));
        xy = [frame.x + (frame.width - (bounds.east - bounds.west) * cosine * scale) / 2 + (lng - bounds.west) * cosine * scale,
          frame.y + (frame.height - (bounds.north - bounds.south) * scale) / 2 + (bounds.north - lat) * scale];
      }
      if (!xy || !xy.every(Number.isFinite) || seen.has(destination.id)) continue;
      seen.add(destination.id);
      result.push({ id: destination.id, xy, number: result.length + 1, label: destination.label, place });
    }
  }
  return result;
}

function handbookMapLayout(day, source, options = {}) {
  const points = handbookRoutePoints(day, source);
  const visits = day.schedule.flatMap(item => handbookSchedulePlaces(item).map(destination => points.find(p => p.id===destination.id)).filter(Boolean))
    .filter((point,index,list) => !index || point!==list[index-1]);
  const width = options.width || 400, unit = 1000 / Math.max(240, width), radius = 14 * unit;
  const canvas = source.canvas || { width: 1448, height: 1086 };
  const frame = source.projection?.frame || { x: 0, y: 0, width: canvas.width, height: canvas.height };
  const xs = points.map(p => p.xy[0]), ys = points.map(p => p.xy[1]);
  const extent = options.whole || !points.length ? [frame.x, frame.y, frame.x + frame.width, frame.y + frame.height]
    : [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)];
  const w = Math.max(extent[2] - extent[0], 1), h = Math.max(extent[3] - extent[1], 1);
  const scale = Math.min((900 - radius * 2) / w, (480 - radius * 2) / h);
  const ox = 500 - (extent[0] + extent[2]) / 2 * scale, oy = 320 - (extent[1] + extent[3]) / 2 * scale;
  const project = xy => [ox + xy[0] * scale, oy + xy[1] * scale];
  const center = list => ({ points: list, xy: project([list.reduce((n,p) => n+p.xy[0], 0)/list.length, list.reduce((n,p) => n+p.xy[1], 0)/list.length]) });
  let groups = points.map(p => center([p])), merged = true;
  while (merged) {
    merged = false;
    outer: for (let i=0; i<groups.length; i++) for (let j=i+1; j<groups.length; j++) {
      if (Math.hypot(groups[i].xy[0]-groups[j].xy[0], groups[i].xy[1]-groups[j].xy[1]) < 2*radius+9*unit) {
        groups[i] = center([...groups[i].points, ...groups[j].points]); groups.splice(j,1); merged = true; break outer;
      }
    }
  }
  const expanding = groups.filter(g => g.points.length > 1 && g.points.some(p => options.focus?.includes(p.id)));
  const fixed = groups.filter(g => !expanding.includes(g)), occupied = fixed.map(g => g.xy);
  const gap = 2*radius+10*unit, min = radius+20*unit;
  for (const group of expanding) for (const point of [...group.points].sort((a,b) => a.number-b.number)) {
    const anchor = project(point.xy), candidates = [anchor];
    for (let y=min; y<=640-min; y+=gap) for (let x=min; x<=1000-min; x+=gap) candidates.push([x,y]);
    const xy = candidates.filter(p => p[0]>=min && p[0]<=1000-min && p[1]>=min && p[1]<=640-min && occupied.every(q => Math.hypot(q[0]-p[0],q[1]-p[1])>=gap-.01))
      .sort((a,b) => Math.hypot(a[0]-anchor[0],a[1]-anchor[1])-Math.hypot(b[0]-anchor[0],b[1]-anchor[1]))[0];
    if (!xy) throw new Error("地图空间不足，无法完整展开地点。");
    occupied.push(xy); fixed.push({ points:[point], xy, anchor });
  }
  if (expanding.length) groups = fixed.sort((a,b) => a.points[0].number-b.points[0].number);
  return { points, visits, groups, unit, radius, frame, scale, ox, oy };
}

function handbookDayMapMarkup(day, options = {}) {
  options = { whole:true, ...options };
  const source = travelMapSourceForDay(state.data.routeMap, day.day);
  if (!source) return `<p class="detail-note">${escapeHtml(window.TravelI18n?.text("当天路线资料待补") || "当天路线资料待补")}</p>`;
  const tr = value => escapeHtml(window.TravelI18n?.text(value) ?? value);
  const m = handbookMapLayout(day, source, options), { groups, points, radius, unit } = m;
  const id = `handbook-map-${day.day}`, canvas = source.canvas || { width:1448, height:1086 };
  const groupFor = point => groups.find(g => g.points.includes(point));
  const lines = m.visits.slice(1).map((p,i) => {
    const a = groupFor(m.visits[i]), b = groupFor(p);
    if (a === b) return "";
    const distance = Math.hypot(b.xy[0]-a.xy[0], b.xy[1]-a.xy[1]);
    const end = b.xy.map((n,k) => n+(a.xy[k]-n)*(radius+6*unit)/distance);
    return `<path d="M${a.xy.join(' ')} L${end.join(' ')}" stroke="#954434" stroke-width="${2*unit}" fill="none" marker-end="url(#${id}-arrow)"/>`;
  }).join("");
  const anchors = groups.filter(g => g.anchor).map(g => `<path d="M${g.anchor.join(' ')} L${g.xy.join(' ')}" stroke="#797d6f" stroke-width="${unit}" stroke-dasharray="${3*unit} ${3*unit}"/><circle cx="${g.anchor[0]}" cy="${g.anchor[1]}" r="${2*unit}" fill="#797d6f"/>`).join("");
  const pins = groups.map(g => {
    const multiple = g.points.length > 1, selected = g.points.some(p => p.id === options.selected);
    const label = multiple ? `${g.points.length} ${window.TravelI18n?.text("个地点") || "个地点"}` : g.points[0].label;
    const action = multiple ? `data-handbook-cluster="${escapeHtml(g.points.map(p=>p.id).join('|'))}"` : `data-handbook-place="${escapeHtml(g.points[0].id)}"`;
    return `<g class="handbook-map-pin" ${action} role="button" tabindex="0" aria-label="${escapeHtml(label)}${multiple ? ' · '+tr("展开全部地点") : ''}"><circle cx="${g.xy[0]}" cy="${g.xy[1]}" r="${radius}" fill="${selected?'#954434':'#fffdf6'}" stroke="#513f31" stroke-width="${1.2*unit}"/><text x="${g.xy[0]}" y="${g.xy[1]+4.5*unit}" text-anchor="middle" font-size="${(multiple?11:14)*unit}" fill="${selected?'white':'#2b2e27'}">${multiple ? g.points.length+(window.TravelI18n?.language==='en'?'':'处') : g.points[0].number}</text><title>${escapeHtml(g.points.map(p=>p.label).join('、'))}</title></g>`;
  }).join("");
  const geographic = source.scope === "geographic-outline" || source.mapMode === "geographic-inset";
  const mapNote = source.disclaimer || (geographic
    ? "地理轮廓与行程地点；彩色连线只表示行程顺序。"
    : "本图为模板化行程示意图，仅表达地点的相对方位与路线顺序，不代表真实比例或精确地理边界。如需使用真实国家或城市地图，可在生成后自行调整。");
  return `<header class="handbook-map-heading"><h3>${tr("当天路线")}</h3><a href="#route">${tr("全旅程地图")} ↗</a></header><div class="handbook-map-tools">${options.focus?.length?`<button type="button" data-handbook-reset>${tr("收起展开地点")}</button>`:''}<button type="button" data-handbook-zoom>${tr(options.whole ? "放大当天路线" : "查看行程区域")}</button></div>
    <svg viewBox="0 0 1000 640" role="group" data-map-mode="${escapeHtml(source.mapMode || "")}" data-map-scope="${escapeHtml(source.scope || "")}" aria-label="${escapeHtml(day.title)} · ${tr("当天路线")}"><defs><clipPath id="${id}-clip"><rect x="${m.frame.x}" y="${m.frame.y}" width="${m.frame.width}" height="${m.frame.height}"/></clipPath><marker id="${id}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0 L10 5 L0 10Z" fill="#954434"/></marker></defs><rect width="1000" height="640" fill="#e5ece7"/><g transform="translate(${m.ox} ${m.oy}) scale(${m.scale})" clip-path="url(#${id}-clip)"><image href="${escapeHtml(source.baseImage)}" width="${canvas.width}" height="${canvas.height}"/></g>${lines}${anchors}${pins}</svg>
    <p class="handbook-map-note">${tr("箭头表示游览顺序；带“处”的圆点可一次展开。")}</p>
    <p class="handbook-map-note" data-authored>${escapeHtml(mapNote)}</p>
    <div class="handbook-map-places" aria-label="${tr("当天地点")}">${points.map(p=>`<div><button type="button" data-handbook-place="${escapeHtml(p.id)}" aria-pressed="${p.id===options.selected}"><b>${p.number}</b><span data-authored>${escapeHtml(p.label)}</span></button>${window.TravelMaps.button(p.id,window.TravelI18n?.text("地图") || "地图",p.place)}</div>`).join('')}</div>
    ${!points.length?`<p class="detail-note">${tr("当天地点坐标待补充。")}</p>`:''}`;
}

function refreshHandbookDayMap(root) {
  const day = state.data.days.find(item => item.day === Number(root.dataset.mapDay));
  if (!day) return;
  const options = handbookMapSelections.get(day.day) || {};
  root.innerHTML = handbookDayMapMarkup(day, { ...options, width:root.clientWidth || 400 });
}

function resetHandbookMapExpansions() {
  for (const [day, options] of handbookMapSelections) {
    if (!options.focus?.length) continue;
    handbookMapSelections.set(day, { ...options, focus:[] });
    const root = document.querySelector(`.handbook-day-map[data-map-day="${day}"]`);
    if (root) refreshHandbookDayMap(root);
  }
}

function setupHandbookMaps() {
  document.addEventListener("click", event => {
    const root = event.target.closest(".handbook-day-map");
    if (root) {
      const target = event.target.closest("[data-handbook-cluster], [data-handbook-place], [data-handbook-reset], [data-handbook-zoom]");
      if (!target) return;
      const day = Number(root.dataset.mapDay), options = { whole:true, ...handbookMapSelections.get(day) };
      if (target.hasAttribute("data-handbook-cluster")) options.focus = target.dataset.handbookCluster.split('|');
      if (target.hasAttribute("data-handbook-place")) { options.selected = target.dataset.handbookPlace; options.focus = [options.selected]; }
      if (target.hasAttribute("data-handbook-reset")) options.focus = [];
      if (target.hasAttribute("data-handbook-zoom")) { options.whole = !options.whole; options.focus = []; }
      handbookMapSelections.set(day, options); refreshHandbookDayMap(root);
      root.closest(".day-card").querySelectorAll(".schedule-item").forEach(item => item.classList.toggle("is-map-selected", item.dataset.schedulePlace===options.selected));
      return;
    }
    const item = event.target.closest(".schedule-item"), card = item?.closest(".day-card");
    if (!card) return;
    resetHandbookMapExpansions();
    const map = card.querySelector(".handbook-day-map"), day = Number(card.dataset.day);
    if (map) {
      handbookMapSelections.set(day, { ...handbookMapSelections.get(day), selected:item.dataset.schedulePlace, focus:item.dataset.schedulePlace ? [item.dataset.schedulePlace] : [] });
      refreshHandbookDayMap(map);
      card.querySelectorAll(".schedule-item").forEach(row => row.classList.toggle("is-map-selected", row===item));
    }
  });
  document.addEventListener("keydown", event => {
    if (["Enter", " "].includes(event.key) && event.target.matches(".handbook-map-pin")) { event.preventDefault(); event.target.dispatchEvent(new MouseEvent("click", { bubbles:true })); }
  });
  const refresh = () => document.querySelectorAll(".handbook-day-map").forEach(refreshHandbookDayMap);
  window.addEventListener("resize", refresh);
  window.addEventListener("travel-runtime:ready", refresh);
  window.addEventListener("travel-language-change", refresh);
  window.addEventListener("travel-view:shown", refresh);
  window.addEventListener("travel-chapter:shown", refresh);
}
