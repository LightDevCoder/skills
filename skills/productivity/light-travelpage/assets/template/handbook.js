(() => {
  let runtimeTodos = null;
  const esc = value => String(value ?? "").replace(/[&<>"']/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
  const tr = value => window.TravelI18n?.text(value) ?? value;
  const words = {
    "行程": "Itinerary", "预订": "Bookings", "账本": "Ledger", "任务": "Tasks", "材料": "Materials",
    "旅行手册章节": "Travel handbook chapters", "选择旅行日期": "Choose a travel date",
    "随身页": "Pocket page", "票据 / 同行": "Documents / companions", "原始材料": "Original materials",
    "住宿资料待补": "Stay details pending", "入住日期待补": "Check-in date pending", "退房日期待补": "Check-out date pending",
    "查看预订资料": "View booking details", "打开同行账本": "Open the shared ledger", "出发前任务": "Before departure",
    "查看全部任务": "View all tasks", "打开原始材料": "Open original materials", "查看票据详情": "View ticket details",
    "已提供原件": "Original provided", "原件待提供": "Original pending", "当前没有附件。": "No attachments yet.",
    "原始车票和确认文件随资料到齐后保存。": "Original tickets and confirmations will appear when supplied.",
    "共同费用": "Shared expenses", "条账单": "bills", "位同行人": "travelers", "查看旅行地图": "Open the trip map", "查看自驾资料": "View driving details"
  };
  window.TravelI18n?.addTranslations(Object.fromEntries(Object.entries(words).map(([source, en]) => [source, { en }])));

  function render() {
    const data = window.TRAVEL_PLAN_DATA;
    const root = document.getElementById("handbook-pocket");
    if (!data || !root) return;
    const modules = window.TRAVEL_PLAN_CONFIG?.modules ?? data.config.modules;
    const bookingsLink = document.getElementById("bookings-navigation-link");
    if (bookingsLink) {
      bookingsLink.hidden = !(modules.flights || modules.accommodations);
      bookingsLink.href = modules.flights ? "#flights" : "#stays";
    }
    const stay = modules.accommodations ? data.accommodations?.[0] : null;
    const snapshot = modules.ledger ? window.TravelLedger?.getSnapshot?.() : null;
    const tickets = data.ticketPlanning?.items ?? [];
    const parts = [];
    if (stay) {
      parts.push(`<section class="pocket-section"><small>${esc(tr("住宿安排"))}</small><h3 data-authored>${esc(stay.name || tr("住宿资料待补"))}</h3><p>${esc(stay.checkIn || tr("入住日期待补"))} — ${esc(stay.checkOut || tr("退房日期待补"))}</p><a href="#stay-${esc(stay.id)}">${esc(tr("查看预订资料"))}</a></section>`);
    }
    if (modules.ledger) {
      parts.push(`<section class="pocket-section"><small>${esc(tr("共同费用"))}</small><p class="pocket-count">${snapshot?.bills?.length ?? 0} <span>${esc(tr("条账单"))}</span></p><p data-no-translate>${esc((snapshot?.travelers ?? []).map(person => person.name).join(" · "))}</p><a href="#ledger">${esc(tr("打开同行账本"))}</a></section>`);
    }
    if (modules.todo) {
      const todos = runtimeTodos ?? data.preTrip?.packingItems ?? [];
      parts.push(`<section class="pocket-section"><h3>${esc(tr("出发前任务"))}</h3><ul>${todos.filter(todo => !todo.completed).slice(0,4).map(todo => `<li data-no-translate>${esc(todo.text)}</li>`).join("")}</ul><a href="#prep">${esc(tr("查看全部任务"))}</a></section>`);
    }
    if (modules.overview || modules.driving) {
      parts.push(`<section class="pocket-section">${modules.overview ? `<a href="#route">${esc(tr("查看旅行地图"))}</a>` : ""}${modules.driving ? `<br><a href="#drive">${esc(tr("查看自驾资料"))}</a>` : ""}</section>`);
    }
    parts.push(`<section class="pocket-section"><h3>${esc(tr("原始材料"))}</h3><p>${tickets.some(ticket => ticket.document?.url || ticket.documentUrl || ticket.booking?.document?.url || ticket.booking?.documentUrl) ? esc(tr("已提供原件")) : esc(tr("当前没有附件。"))}</p><a href="#materials">${esc(tr("打开原始材料"))}</a></section>`);
    root.innerHTML = `<h2 id="pocket-title">${esc(tr("随身页"))}</h2><p class="pocket-subtitle">${esc(tr("票据 / 同行"))}</p>${parts.join("")}`;
    const materials = document.getElementById("handbook-materials");
    if (materials) {
      materials.innerHTML = tickets.length ? tickets.map(ticket => {
        const original = ticket.document?.url || ticket.documentUrl || ticket.booking?.document?.url || ticket.booking?.documentUrl;
        return `<article class="material-record"><h3 data-authored>${esc(ticket.name || ticket.attraction?.nameZh || ticket.attraction?.name || tr("门票详情"))}</h3><p>${esc(tr(original ? "已提供原件" : "原件待提供"))}</p><button type="button" data-ticket-open="${esc(ticket.id)}">${esc(tr("查看票据详情"))}</button></article>`;
      }).join("") : `<div class="material-empty"><p>${esc(tr("当前没有附件。"))}</p><p>${esc(tr("原始车票和确认文件随资料到齐后保存。"))}</p></div>`;
    }
    window.TravelI18n?.apply();
  }

  window.addEventListener("travel-config:ready", render);
  window.addEventListener("travel-runtime:ready", event => { runtimeTodos = event.detail?.todos ?? runtimeTodos; render(); });
  window.addEventListener("travel-language-change", render);
  document.addEventListener("travel-ledger:changed", render);
})();
