/* Lightweight PDF enhancement for the existing ticket dialog. */
(() => {
  const ticketDocuments = new Map();
  const pdfFrames = new Map();
  const warmedDocuments = new Set();

  const isPdf = (documentData) => documentData && (
    String(documentData.type || "").toLowerCase() === "application/pdf" ||
    /\.pdf(?:$|[?#])/i.test(String(documentData.url || ""))
  );

  function indexTicketDocuments(data) {
    ticketDocuments.clear();
    for (const ticket of data?.ticketPlanning?.items || []) ticketDocuments.set(ticket.id, ticket);
  }

  function frameCache() {
    let cache = document.getElementById("ticket-pdf-frame-cache");
    if (!cache) {
      cache = document.createElement("div");
      cache.id = "ticket-pdf-frame-cache";
      cache.hidden = true;
      document.body.append(cache);
    }
    return cache;
  }

  function parkCurrentFrame(body) {
    const current = body?.querySelector(".ticket-dialog__preview--pdf");
    if (current) frameCache().append(current);
  }

  function pdfFrame(ticket, label) {
    const url = String(ticket.document.url);
    let frame = pdfFrames.get(url);
    if (!frame) {
      frame = document.createElement("iframe");
      frame.className = "ticket-dialog__preview ticket-dialog__preview--pdf";
      frame.src = `${url}#view=FitH&toolbar=1`;
      frame.referrerPolicy = "no-referrer";
      pdfFrames.set(url, frame);
    }
    frame.title = `${label} PDF`;
    return frame;
  }

  function warmPdf(url) {
    try {
      const target = new URL(url, window.location.href);
      if (target.origin !== window.location.origin || warmedDocuments.has(target.href)) return;
      warmedDocuments.add(target.href);
      fetch(target.href, { cache: "force-cache" })
        .then((response) => response.ok ? response.blob() : null)
        .catch(() => warmedDocuments.delete(target.href));
    } catch {
      // External or malformed URLs remain available through the normal iframe path.
    }
  }

  function openPdf(ticket) {
    const dialog = document.getElementById("ticket-dialog");
    const body = document.getElementById("ticket-dialog-body");
    const title = document.getElementById("ticket-dialog-title");
    if (!dialog || !body || !title) return;

    const label = ticket.attraction?.nameZh || ticket.attraction?.name || ticket.document.label || "门票 PDF";
    title.textContent = label;
    const url = String(ticket.document.url);
    const frame = pdfFrame(ticket, label);
    if (body.dataset.pdfUrl === url && body.contains(frame)) {
      if (!dialog.open) dialog.showModal();
      return;
    }

    parkCurrentFrame(body);
    body.replaceChildren();
    body.dataset.pdfUrl = url;

    const status = document.createElement("p");
    status.className = "ticket-dialog__status";
    status.textContent = ticket.purchaseStatus === "purchased" ? "已购票" : "门票文件";

    const links = document.createElement("div");
    links.className = "ticket-dialog__links";
    const external = document.createElement("a");
    external.href = ticket.document.url;
    external.target = "_blank";
    external.rel = "noopener noreferrer";
    external.textContent = "在新窗口打开 PDF ↗";
    links.append(external);
    body.append(status, frame, links);
    if (!dialog.open) dialog.showModal();
  }

  if (window.TRAVEL_PLAN_DATA) indexTicketDocuments(window.TRAVEL_PLAN_DATA);
  document.addEventListener("travel-data-ready", (event) => indexTicketDocuments(event.detail));
  const warmFromEvent = (event) => {
    const opener = event.target.closest?.(".schedule-ticket__open");
    const card = opener?.closest("[data-ticket-id]");
    const ticket = card ? ticketDocuments.get(card.dataset.ticketId) : null;
    if (ticket && isPdf(ticket.document)) warmPdf(ticket.document.url);
  };
  document.addEventListener("pointerover", warmFromEvent, true);
  document.addEventListener("focusin", warmFromEvent, true);
  document.addEventListener("touchstart", warmFromEvent, { capture: true, passive: true });
  document.addEventListener("click", (event) => {
    const opener = event.target.closest?.(".schedule-ticket__open");
    const card = opener?.closest("[data-ticket-id]");
    const ticket = card ? ticketDocuments.get(card.dataset.ticketId) : null;
    if (!opener) return;
    if (!ticket || !isPdf(ticket.document)) {
      const body = document.getElementById("ticket-dialog-body");
      parkCurrentFrame(body);
      if (body) delete body.dataset.pdfUrl;
      return;
    }
    event.preventDefault();
    event.stopImmediatePropagation();
    openPdf(ticket);
  }, true);
})();
