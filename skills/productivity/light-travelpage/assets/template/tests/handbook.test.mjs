import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { Window } from "happy-dom";

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

test("date selection shows the supplied day without rebuilding original ticket controls", t => {
  const w = new Window({ url: "http://localhost/" });
  t.after(() => w.happyDOM.abort());
  w.document.body.innerHTML = '<div id="day-count"></div><div id="handbook-dates"></div><div id="timeline"></div>';
  w.TravelMaps = { button: () => "" };
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
  w.document.querySelector('[data-handbook-day="2"]').click();
  assert.equal(second.querySelector(".day-detail").hidden, false);
  assert.match(second.textContent, /15:00[\s\S]*Temple/);
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
