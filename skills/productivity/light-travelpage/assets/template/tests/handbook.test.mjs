import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { Window } from "happy-dom";
import { validateTrip } from "../scripts/validate.mjs";

const read = name => readFileSync(new URL("../" + name, import.meta.url), "utf8");
function page(t, modules) {
  const w = new Window({ url: "http://localhost/" });
  t.after(() => w.happyDOM.abort());
  w.scrollTo = () => {};
  w.HTMLElement.prototype.scrollIntoView = () => {};
  w.document.body.dataset.layout = "handbook";
  w.document.body.innerHTML = `<a id="skip-link"></a><a id="wordmark" href="#top"></a>
    <details id="travel-navigation"><summary id="travel-navigation-trigger">Travel</summary><div class="travel-navigation-menu"></div></details>
    <nav class="handbook-tabs"><a href="#itinerary" data-chapter="itinerary">Itinerary</a><a id="bookings-navigation-link" href="#stays" data-chapter="bookings">Bookings</a><a id="ledger-navigation-link" href="#ledger" data-chapter="ledger">Ledger</a><a href="#materials" data-chapter="materials">Materials</a></nav>
    <main id="main" data-site-view="travel"><section id="itinerary" data-module="itinerary">Original itinerary</section><section id="flights" data-module="flights">Flights</section><section id="stays" data-module="accommodations"><article id="stay-one">Original stay</article></section><section id="route" data-module="overview">Map</section><section id="drive" data-module="driving">Driving</section><section id="prep" data-module="todo"><input value="unsent task"></section><section id="materials" hidden><div id="handbook-materials"></div></section></main>
    <main id="ledger-view" data-site-view="ledger" hidden><input id="ledger-draft" value="unsent bill"></main><aside id="handbook-pocket"></aside>`;
  w.TRAVEL_PLAN_CONFIG = { modules };
  w.eval(read("site-navigation.js"));
  w.document.dispatchEvent(new w.Event("DOMContentLoaded"));
  return w;
}

test("chapters and deep stay links retain drafts and respect disabled modules", async t => {
  const modules = { itinerary: true, accommodations: true, flights: false, ledger: true, todo: true, overview: false, driving: false };
  const w = page(t, modules);
  assert.equal(w.document.querySelector("#itinerary").hidden, false);
  assert.equal(w.document.querySelector("#stays").hidden, true);
  w.document.querySelector("#bookings-navigation-link").click();
  assert.equal(w.document.querySelector("#stays").hidden, false);
  assert.equal(w.document.querySelector("#flights").hidden, true);
  w.document.querySelector("#ledger-navigation-link").click();
  assert.equal(w.document.querySelector("#ledger-view").hidden, false);
  w.document.querySelector('[href="#materials"]').click();
  assert.equal(w.document.querySelector("#main").hidden, false);
  assert.equal(w.document.querySelector("#materials").hidden, false);
  assert.equal(w.document.querySelector("#ledger-draft").value, "unsent bill");
  assert.equal(w.document.querySelector("#prep input").value, "unsent task");
  w.history.pushState({}, "", "#stay-one");
  w.dispatchEvent(new w.Event("popstate"));
  await new Promise(resolve => setTimeout(resolve, 40));
  assert.equal(w.document.querySelector("#stays").hidden, false);
  assert.equal(w.document.body.dataset.chapter, "bookings");
});

test("material-only draft remains useful when all travel modules are disabled", t => {
  const w = page(t, { itinerary: false, accommodations: false, flights: false, ledger: false, todo: false, overview: false, driving: false });
  w.document.querySelector("#ledger-navigation-link").hidden = true;
  w.dispatchEvent(new w.Event("travel-config:ready"));
  assert.equal(w.document.querySelector("#materials").hidden, false);
  assert.equal(w.document.querySelector("#itinerary").hidden, true);
  assert.equal(w.document.querySelector("#ledger-view").hidden, true);
});

test("date pages switch instantly while retaining every supplied day and original controls", t => {
  const w = new Window({ url: "http://localhost/" });
  t.after(() => w.happyDOM.abort());
  w.document.body.innerHTML = '<div id="day-count"></div><div id="handbook-dates"></div><div id="timeline"></div>';
  const scrolls = [];
  w.scrollTo = options => scrolls.push(options);
  w.HTMLElement.prototype.scrollIntoView = () => assert.fail("date switching must not animate down the feed");
  w.TravelMaps = { button: () => "" };
  w.eval(read("route-ui.js"));
  const data = { days: [
    { day: 1, date: "2099-11-07", title: "Arrive", locations: [], schedule: [{ time: "10:00", text: "Station", type: "note" }] },
    { day: 2, date: "2099-11-08", title: "Walk", locations: [], schedule: [{ time: "15:00", text: "Temple", type: "note" }] }
  ], places: [], restaurants: [], ticketPlanning: { items: [] }, mapLinks: { navigationPolicy: { noNavigationTypes: ["note"], selfNavigationTypes: [] } } };
  w.eval(read("app.js").replace('document.addEventListener("DOMContentLoaded", init);', "") + `\nstate.data=${JSON.stringify(data)};renderTimeline();`);
  const first = w.document.querySelector('.day-card[data-day="1"]');
  const second = w.document.querySelector('.day-card[data-day="2"]');
  assert.equal(first.hidden, false);
  assert.equal(second.hidden, true);
  const originalContent = second.querySelector(".schedule-item");
  w.document.querySelector('[data-handbook-day="2"]').click();
  assert.equal(first.hidden, true);
  assert.equal(second.hidden, false);
  assert.equal(second.querySelector(".schedule-item"), originalContent);
  assert.equal(second.querySelector(".day-detail").hidden, false);
  assert.equal(w.document.querySelectorAll('.day-card:not([hidden])').length, 1);
  assert.ok(scrolls.every(options => options.behavior === "instant"));
  w.eval("renderTimeline()");
  assert.equal(w.document.querySelector('.day-card[data-day="2"]').hidden, false);
  w.document.querySelector('[data-handbook-day="1"]').click();
  assert.equal(w.document.querySelector('.day-card[data-day="1"]').hidden, false);
  assert.equal(w.document.querySelector('.day-card[data-day="2"]').hidden, true);
  w.document.querySelector('[data-handbook-day="2"]').click();
  assert.equal(second.querySelector(".day-detail").hidden, false);
  assert.match(second.textContent, /15:00[\s\S]*Temple/);
});

function mappedPage(t) {
  const w = new Window({ url:"http://localhost/" });
  t.after(() => w.happyDOM.abort());
  w.HTMLElement.prototype.scrollIntoView = () => {};
  w.document.body.innerHTML = '<div id="day-count"></div><div id="handbook-dates"></div><div id="timeline"></div>';
  w.TravelMaps = { button:id => `<button data-place-id="${id}">Map</button>` };
  const places = [
    { id:"outside", name:"Origin", geo:{lat:31,lng:121} },
    { id:"airport", name:"Airport", geo:{lat:42.79,lng:141.68} },
    { id:"station", name:"Station", geo:{lat:43.068,lng:141.350} },
    { id:"hotel", name:"Hotel", geo:{lat:43.0682,lng:141.352} },
    { id:"park", name:"Park", geo:{lat:43.060,lng:141.348} },
    { id:"dinner", name:"Dinner", geo:{lat:43.055,lng:141.353} }
  ];
  const data = { days:[
    { day:1, date:"2099-11-07", title:"Arrive", locations:[], schedule:[...places.map((p,i)=>({id:`first-${i}`,placeId:p.id,type:"walk",time:`${i+10}:00`,text:p.name})),{id:"return",placeId:"hotel",type:"rest",time:"20:00",text:"Return to the same hotel"}] },
    { day:2, date:"2099-11-08", title:"Stay", locations:[], schedule:[{id:"second",placeId:"hotel",type:"walk",time:"10:00",text:"Hotel again"}] }
  ], places, restaurants:[], ticketPlanning:{items:[]}, mapLinks:{navigationPolicy:{noNavigationTypes:["note","rest"],selfNavigationTypes:["walk"]}},
  routeMap:{regions:[{id:"test",days:[1,2],baseImage:"assets/maps/real-outline.svg",canvas:{width:1448,height:1086},projection:{bounds:[140.58,42.34,141.92,43.35],frame:{x:52,y:590,width:530,height:415}},places:[]}]}};
  w.eval(read("overview-map.js")+read("route-ui.js")+read("app.js").replace('document.addEventListener("DOMContentLoaded", init);',"")+`\nstate.data=${JSON.stringify(data)};window.TRAVEL_PLAN_DATA=state.data;state.config={modules:{overview:true}};renderTimeline();setupHandbookMaps();`);
  return w;
}

test("daily maps render directly with all in-region schedule places and one-step cluster expansion", t => {
  const w = mappedPage(t), map = w.document.querySelector('.handbook-day-map[data-map-day="1"]');
  assert.equal(w.document.querySelectorAll('.day-card:not([hidden]) .handbook-day-map').length,1);
  assert.equal(w.document.querySelectorAll('.handbook-day-map').length,2);
  assert.equal(map.querySelectorAll('.handbook-map-places [data-handbook-place]').length,5);
  assert.equal(map.querySelector('[data-handbook-place="outside"]'),null);
  const original = w.document.querySelector('[data-schedule-id="first-2"]');
  map.querySelector('[data-handbook-cluster]').dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
  assert.equal(map.querySelectorAll('svg [data-handbook-cluster]').length,0);
  assert.equal(map.querySelectorAll('svg [data-handbook-place]').length,5);
  map.querySelector('svg [data-handbook-place="hotel"]').dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
  assert.equal(map.querySelectorAll('svg [data-handbook-place]').length,5);
  assert.equal(map.querySelector('.handbook-map-places [data-handbook-place="hotel"]').getAttribute('aria-pressed'),'true');
  assert.equal(w.document.querySelector('[data-schedule-id="first-2"]'),original);
  assert.equal(w.document.querySelectorAll('.day-card:not([hidden])').length,1);
});

test("another schedule item or date collapses expansion while keeping the complete itinerary", t => {
  const w = mappedPage(t), map = w.document.querySelector('.handbook-day-map[data-map-day="1"]');
  map.querySelector('[data-handbook-cluster]').dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
  w.document.querySelector('[data-schedule-id="first-1"] .schedule-text').click();
  assert.equal(map.querySelectorAll('svg [data-handbook-cluster]').length,1);
  assert.equal(map.querySelectorAll('.handbook-map-places [data-handbook-place]').length,5);
  map.querySelector('[data-handbook-cluster]').dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
  w.document.querySelector('[data-handbook-day="2"]').click();
  assert.equal(map.querySelectorAll('svg [data-handbook-cluster]').length,1);
  assert.equal(w.document.querySelectorAll('.day-card:not([hidden]) .day-detail:not([hidden])').length,1);
});

test("daily cluster placement keeps every expanded marker separated at mobile and desktop widths", t => {
  const w = mappedPage(t);
  for (const width of [276,440]) {
    const result = w.eval(`handbookMapLayout(window.TRAVEL_PLAN_DATA.days[0],window.TRAVEL_PLAN_DATA.routeMap.regions[0],{width:${width},focus:['station','hotel','park','dinner']})`);
    assert.equal(result.points.length,5);
    assert.equal(result.groups.length,5);
    assert.deepEqual(Array.from(result.visits,p=>p.id),['airport','station','hotel','park','dinner','hotel']);
    for (let i=0;i<result.groups.length;i++) for(let j=i+1;j<result.groups.length;j++) {
      const a=result.groups[i].xy,b=result.groups[j].xy;
      assert.ok(Math.hypot(a[0]-b[0],a[1]-b[1])>2*result.radius);
    }
  }
});

test("daily maps and original navigation merge and deduplicate primary and multiple place references", t => {
  const w = mappedPage(t);
  const item = { placeId:"hotel", placeIds:["park","park"], type:"walk" };
  const actual = w.eval(`({navigation:navigationDestinations(${JSON.stringify(item)}).map(p=>p.id),map:handbookSchedulePlaces(${JSON.stringify(item)}).map(p=>p.id)})`);
  assert.deepEqual(Array.from(actual.navigation),["park","hotel"]);
  assert.deepEqual(Array.from(actual.map),["park","hotel"]);
});

test("schematic daily maps retain the supplied disclaimer and mode with the place controls", t => {
  const w = mappedPage(t), source = w.TRAVEL_PLAN_DATA.routeMap.regions[0];
  source.scope = "template-schematic";
  source.mapMode = "frozen-template";
  source.disclaimer = "示意布局，不代表真实比例和地理边界。";
  delete source.projection;
  source.places = w.TRAVEL_PLAN_DATA.places.filter(p=>p.id!=="outside").map((p,i)=>({id:p.id,x:100+i*180,y:300}));
  const root = w.document.createElement("div");
  root.innerHTML = w.eval("handbookDayMapMarkup(window.TRAVEL_PLAN_DATA.days[0])");
  assert.ok(root.textContent.includes(source.disclaimer));
  assert.equal(root.querySelector('svg[role="group"]').dataset.mapScope,"template-schematic");
  assert.equal(root.querySelectorAll('.handbook-map-places [data-handbook-place]').length,5);
});

test("pocket and material entries derive from supplied records and escape their values", t => {
  const w = new Window({ url: "http://localhost/" });
  t.after(() => w.happyDOM.abort());
  w.document.body.innerHTML = '<a id="bookings-navigation-link"></a><aside id="handbook-pocket"></aside><div id="handbook-materials"></div>';
  w.TRAVEL_PLAN_CONFIG = { modules: { accommodations: true, flights: false, ledger: false, todo: false } };
  w.TRAVEL_PLAN_DATA = { config: w.TRAVEL_PLAN_CONFIG, accommodations: [{ id: "one", name: "<img src=x onerror=alert(1)>", checkIn: null, checkOut: null }], ticketPlanning: { items: [{ id: 'proof"bad', name: "Source & ticket", document: { url: "assets/tickets/proof.pdf" } }] } };
  w.eval(read("handbook.js"));
  w.dispatchEvent(new w.Event("travel-config:ready"));
  assert.equal(w.document.querySelectorAll("img").length, 0);
  assert.match(w.document.querySelector("#handbook-pocket").textContent, /入住日期待补/);
  assert.match(w.document.querySelector("#handbook-pocket").textContent, /已提供原件/);
  assert.equal(w.document.querySelector("[data-ticket-open]").dataset.ticketOpen, 'proof"bad');
  assert.equal(w.document.querySelectorAll("[data-ticket-open]").length, 1);
  w.TRAVEL_PLAN_DATA.ticketPlanning.items = [];
  w.dispatchEvent(new w.Event("travel-runtime:ready"));
  assert.equal(w.document.querySelectorAll("[data-ticket-open]").length, 0);
  assert.match(w.document.querySelector("#handbook-materials").textContent, /当前没有附件/);
});


test("content anchor preserves the visible chapter and disabled ledger hashes retain a travel chapter", async t => {
  const modules = { itinerary: true, accommodations: true, flights: false, ledger: false, todo: true, overview: false, driving: false };
  const w = page(t, modules);
  w.document.querySelector("#ledger-navigation-link").hidden = true;
  w.document.querySelector("#bookings-navigation-link").click();
  w.location.hash = "#main";
  w.dispatchEvent(new w.Event("hashchange"));
  await new Promise(resolve => setTimeout(resolve, 40));
  assert.equal(w.document.body.dataset.chapter, "bookings");
  assert.equal(w.document.querySelector("#stays").hidden, false);
  w.location.hash = "#ledger-stats";
  w.dispatchEvent(new w.Event("hashchange"));
  await new Promise(resolve => setTimeout(resolve, 40));
  assert.equal(w.document.querySelector("#main").hidden, false);
  assert.equal(w.document.querySelector("#itinerary").hidden, false);
});

test("demo navigation remains in the travel main when the handbook footer is outside it", t => {
  const w = new Window({ url: "http://localhost/" });
  t.after(() => w.happyDOM.abort());
  w.document.body.innerHTML = read("index.html").split(/<body[^>]*>/)[1].split("</body>")[0];
  w.TravelMaps = { button: id => `<button data-place="${id}">Map</button>` };
  w.eval(read("travel-cards.js"));
  w.document.dispatchEvent(new w.CustomEvent("travel-data-ready", { detail: {
    config: { demo: true, modules: { accommodations: false } }, accommodations: [],
    places: [{ id: "demo-place", name: "Public test place" }], demoNavigationPlaceIds: ["demo-place"], ticketPlanning: { items: [] }
  } }));
  assert.equal(w.document.querySelector("#map-examples").parentElement.id, "main");
  assert.equal(w.document.querySelector("#map-examples [data-place]").dataset.place, "demo-place");
  assert.match(w.document.querySelector(".demo-notice").textContent, /虚构示例/);
});


test("browser history restores the chapter belonging to a content-anchor entry", async t => {
  const w = page(t, { itinerary: true, accommodations: true, flights: false, ledger: false, todo: true, overview: false, driving: false });
  w.document.querySelector("#bookings-navigation-link").click();
  w.location.hash = "#main";
  w.dispatchEvent(new w.Event("hashchange"));
  await new Promise(resolve => setTimeout(resolve, 40));
  assert.equal(w.document.body.dataset.chapter, "bookings");
  const mainEntry = structuredClone(w.history.state);
  assert.equal(mainEntry.handbookChapter, "bookings");
  const tasks = w.document.createElement("a");
  tasks.href = "#prep";
  w.document.querySelector(".handbook-tabs").append(tasks);
  tasks.click();
  assert.equal(w.document.body.dataset.chapter, "todo");
  w.history.replaceState(mainEntry, "", "#main");
  w.dispatchEvent(new w.Event("popstate"));
  await new Promise(resolve => setTimeout(resolve, 40));
  assert.equal(w.document.body.dataset.chapter, "bookings");
  assert.equal(w.document.querySelector("#stays").hidden, false);
  assert.equal(w.document.querySelector("#prep").hidden, true);
});

function realNavigationPage(t, modules) {
  const w = new Window({ url: "http://localhost/" });
  t.after(() => w.happyDOM.abort());
  w.HTMLElement.prototype.scrollIntoView = () => {};
  w.scrollTo = () => {};
  w.document.write(read("index.html").replace(/<script\b[^>]*>[\s\S]*?<\/script>/g, ""));
  w.TRAVEL_PLAN_CONFIG = { modules };
  w.eval(read("app.js").replace('document.addEventListener("DOMContentLoaded", init);', "") +
    `\nstate.config=${JSON.stringify({ modules, persistence: { mode: "local" } })};applyModuleConfig();`);
  w.eval(read("site-navigation.js"));
  w.document.dispatchEvent(new w.Event("DOMContentLoaded"));
  return w;
}

test("real chapter navigation exposes route and puts only unrepresented destinations in More", t => {
  const modules = { itinerary:true, flights:true, accommodations:true, overview:true, ledger:true, todo:true, driving:true };
  const w = realNavigationPage(t, modules);
  const visibleHrefs = selector => [...w.document.querySelectorAll(selector)].filter(e => !e.hidden).map(e => e.getAttribute("href"));
  assert.deepEqual(visibleHrefs(".handbook-tabs a"), ["#itinerary", "#flights", "#ledger", "#prep", "#route"]);
  assert.deepEqual(visibleHrefs(".travel-navigation-menu a"), ["#materials", "#drive"]);
  w.document.querySelector("#todo-input").value = "unsaved checklist draft";
  w.document.querySelector('.handbook-tabs [href="#route"]').click();
  assert.equal(w.document.querySelector("#route").hidden, false);
  assert.equal(w.document.querySelector("#itinerary").hidden, true);
  w.document.querySelector('.travel-navigation-menu [href="#materials"]').click();
  assert.equal(w.document.querySelector("#materials").hidden, false);
  assert.equal(w.document.querySelector('.travel-navigation-menu [href="#materials"]').getAttribute("aria-current"), "page");
  assert.equal(w.document.querySelector("#todo-input").value, "unsaved checklist draft");
});

test("materials-only navigation is a direct topbar link and preserves chapter routing", t => {
  const modules = { itinerary:false, flights:false, accommodations:false, overview:false, ledger:false, todo:false, driving:false };
  const w = realNavigationPage(t, modules);
  assert.equal(w.document.querySelector("#travel-navigation").hidden, true);
  assert.equal(w.document.querySelector("#materials-navigation-link").hidden, false);
  w.document.querySelector("#materials-navigation-link").click();
  assert.equal(w.location.hash, "#materials");
  assert.equal(w.document.querySelector("#materials-navigation-link").getAttribute("aria-current"), "page");
  assert.deepEqual([...w.document.querySelectorAll(".handbook-tabs a")].filter(e => !e.hidden), []);
  assert.deepEqual([...w.document.querySelectorAll(".travel-navigation-menu a")].filter(e => !e.hidden).map(e => e.getAttribute("href")), ["#materials"]);
  assert.equal(w.document.querySelector("#materials").hidden, false);
});


test("selecting a clustered place from the schedule or place list expands it and preserves every location", t => {
  const w = mappedPage(t), map = w.document.querySelector('.handbook-day-map[data-map-day="1"]');
  assert.equal(map.querySelector('svg [data-handbook-place="station"]'), null);
  w.document.querySelector('[data-schedule-id="first-2"] .schedule-text').click();
  assert.equal(map.querySelectorAll('svg [data-handbook-place]').length, 5);
  assert.ok(map.querySelector('svg [data-handbook-place="station"]'));
  assert.equal(map.querySelector('.handbook-map-places [data-handbook-place="station"]').getAttribute('aria-pressed'), 'true');
  w.document.querySelector('[data-schedule-id="first-1"] .schedule-text').click();
  assert.equal(map.querySelectorAll('svg [data-handbook-cluster]').length, 1);
  map.querySelector('.handbook-map-places [data-handbook-place="hotel"]').click();
  assert.equal(map.querySelectorAll('svg [data-handbook-place]').length, 5);
  assert.equal(map.querySelectorAll('.handbook-map-places [data-handbook-place]').length, 5);
  assert.equal(map.querySelector('.handbook-map-places [data-handbook-place="hotel"]').getAttribute('aria-pressed'), 'true');
});


test("validated undated draft initializes itinerary and map and switches its daily page", async t => {
  const data = JSON.parse(read("trip-data.json"));
  data.metadata.tripId = "undated-init";
  Object.assign(data.trip, {status:"draft",startDate:null,endDate:null,dayCount:2});
  Object.assign(data.config.modules, {itinerary:true,overview:true});
  data.places = [{id:"a",name:"Station",geo:{lat:43,lng:141}}, {id:"b",name:"Hotel",geo:{lat:43.01,lng:141.01}}];
  data.days = [1,2].map(day=>({day,date:null,title:`Day ${day}`,locations:[],schedule:[
    {id:`visit-${day}-a`,time:"10:00",text:"Station",type:"walk",placeId:"a"},
    {id:`visit-${day}-b`,time:"11:00",text:"Hotel",type:"walk",placeId:"b"}
  ]}));
  data.map.places = data.places;
  data.map.routes = [1,2].map(day=>({day,placeIds:["a","b"]}));
  data.routeMap = {regions:[{id:"draft-map",days:[1,2],mapMode:"frozen-template",scope:"template-schematic",disclaimer:"Schematic test map",canvas:{width:1000,height:640},baseImage:"assets/maps/templates/template-03-coastal.webp",places:[{id:"a",x:300,y:300},{id:"b",x:600,y:300}],routes:data.map.routes}]};
  const validation = validateTrip(data,new URL("../",import.meta.url).pathname);
  assert.equal(validation.ok,true,validation.errors.join("\n"));
  const w = new Window({url:"http://localhost/"});
  t.after(()=>w.happyDOM.abort());
  const errors = [];
  w.console.error=(...args)=>errors.push(args.map(String).join(" "));
  w.document.write(read("index.html").replace(/<script\b[^>]*>[\s\S]*?<\/script>/g,"").replace(/<link[^>]+rel="stylesheet"[^>]*>/g,""));
  w.HTMLElement.prototype.scrollIntoView=()=>{}; w.scrollTo=()=>{};
  w.fetch=async url=>({ok:true,json:async()=>String(url)==="trip-data.json"?structuredClone(data):({version:1,revision:0,todos:[],tickets:[],bills:[],travelers:[],settings:null})});
  w.TravelMaps={button:()=>""};
  w.eval(read("runtime-storage.js"));
  await w.eval(read("travel-cards.js")+"\n"+read("overview-map.js")+"\n"+read("route-ui.js")+"\n"+read("app.js").replace('document.addEventListener("DOMContentLoaded", init);',"")+"\ninit();");
  assert.equal(w.document.querySelector("#loading-error").hidden,true,errors.join("\n"));
  assert.equal(w.document.querySelectorAll(".day-card").length,2);
  assert.equal(w.document.querySelectorAll(".handbook-day-map").length,2);
  assert.deepEqual([...w.document.querySelectorAll(".route-day-tabs button")].map(e=>e.textContent),["总览","DAY 1","DAY 2"]);
  w.document.querySelector('[data-handbook-day="2"]').click();
  assert.equal(w.document.querySelector('.day-card[data-day="2"]').hidden,false);
  assert.equal(w.document.querySelector('.day-card[data-day="1"]').hidden,true);
  w.document.querySelector('[data-route-day="2"]').click();
  assert.equal(w.document.querySelector('[data-route-day="2"]').getAttribute("aria-pressed"),"true");
  assert.equal(w.document.querySelectorAll(".map-place-dot").length,2);
  assert.deepEqual(errors,[]);
});
