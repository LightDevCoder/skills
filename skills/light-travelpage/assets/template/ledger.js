import { CURRENCY_CATALOG } from "./currencies.js";
(() => {
  "use strict";
  window.TravelI18n?.addTranslations(Object.fromEntries(CURRENCY_CATALOG.map(c => [c.nameZh, {en:c.nameEn}])));

  const STORAGE_VERSION = 1;
  const DEFAULT_SETTINGS = Object.freeze({
    baseCurrency: "CNY",
    commonCurrencies: ["EUR", "CHF", "HKD"],
    lastCurrency: "CNY"
  });
  const CATEGORIES = Object.freeze(["餐饮", "交通", "住宿", "门票", "购物", "其他"]);
  const AVATAR_COLORS = Object.freeze([
    "#D96C42", "#217D91", "#5C8E62", "#8B6AA8", "#C58B32",
    "#4F72A2", "#B85F76", "#4E8F86", "#9A6B4F", "#68798E"
  ]);

  // The picker searches every field, so the complete catalog can stay out of view
  // until a traveler asks for a particular currency.

  const CURRENCY_BY_CODE = new Map(CURRENCY_CATALOG.map((currency) => [currency.code, currency]));
  const currencySearchText = new Map(CURRENCY_CATALOG.map((currency) => [
    currency.code,
    normalizeSearch([currency.code, currency.nameZh, currency.nameEn, currency.symbol, currency.aliases].join(" "))
  ]));

  let ledgerRoot = null;
  let ledgerTripId = "";
  let ledgerAdapter = null;
  let ledgerPersistenceMode = "local";
  let ledgerData = null;
  let initialized = false;
  let activeTab = "entry";
  let editingBillId = null;
  let openDialogName = null;
  let currencyPickerMode = "common";
  let currencyQuery = "";
  let notice = "";
  let billDraft = null;
  let editDraft = null;
  let recoveredMutation = null;
  let draftGeneration = 0;
  let renderDirty = false;
  let editingMemberId = null;
  let editingNoteBillId = null;
  let pendingNoteSave = null;
  let noteOpenRequest = 0;
  let mutationQueue = Promise.resolve();

  function normalizeSearch(value) {
    return String(value || "")
      .normalize("NFKD")
      .toLocaleLowerCase()
      .replace(/[\s._/-]+/g, "");
  }

  function escapeHtml(value = "") {
    return String(value).replace(/[&<>"']/g, (character) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      "\"": "&quot;",
      "'": "&#39;"
    })[character]);
  }

  function escapeAttribute(value = "") {
    return escapeHtml(value).replace(/`/g, "&#96;");
  }

  function deepClone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function makeId(prefix) {
    if (globalThis.crypto && typeof globalThis.crypto.randomUUID === "function") {
      return `${prefix}-${globalThis.crypto.randomUUID()}`;
    }
    return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
  }

  function avatarInitial(name) {
    const characters = Array.from(String(name || "").trim());
    if (!characters.length) return "?";
    const firstHanIndex = characters.findIndex((character) => /\p{Script=Han}/u.test(character));
    if (firstHanIndex >= 0) {
      const firstHan = characters[firstHanIndex];
      if (["小", "阿", "老"].includes(firstHan)) {
        const nextHan = characters.slice(firstHanIndex + 1).find((character) => /\p{Script=Han}/u.test(character));
        if (nextHan) return nextHan;
      }
      return firstHan;
    }
    const latin = characters.find((character) => /[A-Za-z]/.test(character));
    return latin ? latin.toUpperCase() : characters[0].toUpperCase();
  }

  function nextAvatarColor(travelers) {
    const used = new Set(travelers.map((traveler) => traveler.color.toUpperCase()));
    return AVATAR_COLORS.find((color) => !used.has(color.toUpperCase()))
      || AVATAR_COLORS[travelers.length % AVATAR_COLORS.length];
  }

  function isValidColor(value) {
    return /^#[0-9a-f]{6}$/i.test(String(value || ""));
  }

  function toCents(value) {
    const normalized = String(value ?? "").trim().replace(/,/g, "");
    if (!/^(?:\d+|\d*\.\d{1,2})$/.test(normalized)) return null;
    const [whole = "0", fraction = ""] = normalized.split(".");
    const cents = Number(whole) * 100 + Number(fraction.padEnd(2, "0"));
    return Number.isSafeInteger(cents) ? cents : null;
  }

  function centsToInput(cents) {
    if (!Number.isSafeInteger(cents)) return "";
    return (cents / 100).toFixed(2);
  }

  function formatMoney(cents, currencyCode) {
    const amount = Number(cents || 0) / 100;
    try {
      return new Intl.NumberFormat(window.TravelI18n?.language || "zh-CN", {
        style: "currency",
        currency: currencyCode,
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(amount);
    } catch {
      return `${currencyCode} ${amount.toFixed(2)}`;
    }
  }

  function defaultData() {
    return {
      version: STORAGE_VERSION,
      settings: deepClone(DEFAULT_SETTINGS),
      travelers: [],
      bills: [],
      updatedAt: new Date().toISOString()
    };
  }

  function normalizeData(raw) {
    const fallback = defaultData();
    if (!raw || typeof raw !== "object") return fallback;
    const rawTravelers = Array.isArray(raw.travelers) ? raw.travelers : [];
    const usedIds = new Set();
    const travelers = rawTravelers.flatMap((traveler, index) => {
      const name = String(traveler?.name || "").trim().slice(0, 30);
      let id = String(traveler?.id || "").trim();
      if (!name) return [];
      if (!id || usedIds.has(id)) id = makeId("person");
      usedIds.add(id);
      const color = isValidColor(traveler?.color)
        ? traveler.color.toUpperCase()
        : AVATAR_COLORS[index % AVATAR_COLORS.length];
      return [{ id, name, initial: avatarInitial(name), color }];
    });
    const travelerIds = new Set(travelers.map((traveler) => traveler.id));
    const requestedBase = String(raw.settings?.baseCurrency || DEFAULT_SETTINGS.baseCurrency).toUpperCase();
    const baseCurrency = CURRENCY_BY_CODE.has(requestedBase) ? requestedBase : DEFAULT_SETTINGS.baseCurrency;
    const commonCurrencies = [...new Set(
      (Array.isArray(raw.settings?.commonCurrencies) ? raw.settings.commonCurrencies : DEFAULT_SETTINGS.commonCurrencies)
        .map((code) => String(code).toUpperCase())
        .filter((code) => CURRENCY_BY_CODE.has(code) && code !== baseCurrency)
    )];
    const availableCurrencies = new Set([baseCurrency, ...commonCurrencies]);
    const requestedLast = String(raw.settings?.lastCurrency || baseCurrency).toUpperCase();
    const lastCurrency = availableCurrencies.has(requestedLast) ? requestedLast : baseCurrency;
    const bills = (Array.isArray(raw.bills) ? raw.bills : []).flatMap((bill) => {
      const originalAmountCents = Number(bill?.originalAmountCents);
      const baseAmountCents = Number(bill?.baseAmountCents);
      const currency = String(bill?.currency || baseCurrency).toUpperCase();
      const payerId = String(bill?.payerId || "");
      const participantIds = [...new Set(Array.isArray(bill?.participantIds) ? bill.participantIds.map(String) : [])]
        .filter((id) => travelerIds.has(id));
      if (!Number.isSafeInteger(originalAmountCents) || originalAmountCents <= 0) return [];
      if (!Number.isSafeInteger(baseAmountCents) || baseAmountCents <= 0) return [];
      if (!CURRENCY_BY_CODE.has(currency) || !travelerIds.has(payerId) || !participantIds.length) return [];
      const category = CATEGORIES.includes(bill?.category) ? bill.category : "其他";
      return [{
        id: String(bill.id || makeId("bill")),
        originalAmountCents,
        baseAmountCents,
        currency,
        category,
        note: typeof bill.note === "string" ? bill.note.trim().slice(0, 160) : "",
        orderedAt: typeof bill.orderedAt === "string" ? bill.orderedAt : "",
        payerId,
        participantIds,
        createdAt: typeof bill.createdAt === "string" ? bill.createdAt : new Date().toISOString(),
        updatedAt: typeof bill.updatedAt === "string" ? bill.updatedAt : new Date().toISOString()
      }];
    });
    return {
      version: STORAGE_VERSION,
      settings: { baseCurrency, commonCurrencies, lastCurrency },
      travelers,
      bills,
      updatedAt: typeof raw.updatedAt === "string" ? raw.updatedAt : fallback.updatedAt
    };
  }

  function createLocalStorageAdapter(tripId, options = {}) {
    const runtimeStorage = globalThis.TravelRuntimeStorage;
    if (runtimeStorage?.createAdapter) {
      return runtimeStorage.createAdapter({
        ...options,
        mode: "local",
        tripId,
        collections: ["settings", "travelers", "bills"]
      });
    }

    const storageKey = options.storageKey
      || `travel-plan:runtime:v1:${encodeURIComponent(String(tripId || "default-trip"))}`;
    let memorySnapshot = null;
    let storage = options.storage;
    if (!storage) {
      try {
        storage = globalThis.localStorage || null;
      } catch {
        storage = null;
      }
    }

    function readSnapshot() {
      if (!storage) return memorySnapshot ? deepClone(memorySnapshot) : null;
      try {
        const serialized = storage.getItem(storageKey);
        if (!serialized) return memorySnapshot ? deepClone(memorySnapshot) : null;
        const parsed = JSON.parse(serialized);
        memorySnapshot = parsed && typeof parsed === "object" ? parsed : null;
        return memorySnapshot ? deepClone(memorySnapshot) : null;
      } catch (error) {
        console.warn("TravelLedger could not read localStorage; using memory for this tab.", error);
        storage = null;
        return memorySnapshot ? deepClone(memorySnapshot) : null;
      }
    }

    function writeSnapshot(next) {
      const previous = readSnapshot() || {};
      const snapshot = {
        ...previous,
        version: STORAGE_VERSION,
        settings: deepClone(next.settings),
        travelers: deepClone(next.travelers),
        bills: deepClone(next.bills),
        updatedAt: next.updatedAt
      };
      memorySnapshot = snapshot;
      if (storage) {
        try {
          storage.setItem(storageKey, JSON.stringify(snapshot));
        } catch (error) {
          console.warn("TravelLedger could not write localStorage; using memory for this tab.", error);
          storage = null;
        }
      }
      Object.assign(next, deepClone(snapshot));
      return deepClone(snapshot);
    }

    return {
      mode: "local",
      tripId,
      storageKey,
      async load() {
        return readSnapshot();
      },
      async save(next) {
        return writeSnapshot(next);
      }
    };
  }

  function createD1Adapter(tripId, options = {}) {
    const runtimeStorage = globalThis.TravelRuntimeStorage;
    if (runtimeStorage?.createAdapter) {
      return runtimeStorage.createAdapter({
        ...options,
        mode: "d1",
        tripId,
        collections: ["settings", "travelers", "bills"]
      });
    }
    let previous = null;
    const collections = ["bills", "travelers"];
    const rawApiBase = String(options.apiBase || "/api/trip").trim();
    if (!/^\/(?!\/)/.test(rawApiBase) || rawApiBase.includes("\\") || /[?#]/.test(rawApiBase)) {
      throw new Error("D1 apiBase must be a same-origin absolute path");
    }
    const apiBase = rawApiBase.replace(/\/+$/, "") || "/";
    const endpoint = `${apiBase}/${encodeURIComponent(tripId)}?collections=bills%2Ctravelers`;
    return {
      mode: "d1",
      async load() {
        const response = await fetch(endpoint, { cache: "no-store" });
        if (!response.ok) throw new Error(`API ${response.status}`);
        previous = await response.json();
        return previous;
      },
      async save(next) {
        const changes = [];
        for (const collection of collections) {
          const before = new Map((previous?.[collection] || []).map((item) => [item.id, item]));
          const after = new Map((next[collection] || []).map((item) => [item.id, item]));
          before.forEach((_, id) => { if (!after.has(id)) changes.push({ op: "delete", collection, id }); });
          after.forEach((value, id) => {
            if (JSON.stringify(before.get(id)) !== JSON.stringify(value)) changes.push({ op: "upsert", collection, id, value });
          });
        }
        const response = await fetch(endpoint, {
          method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ changes })
        });
        if (!response.ok) throw new Error(`API ${response.status}`);
        previous = await response.json();
        // The server is authoritative and merges record-level changes atomically.
        Object.assign(next, previous);
      }
    };
  }

  async function resolveTripConfig(root, options) {
    if (options.config && typeof options.config === "object") return options.config;
    if (globalThis.TRAVEL_PLAN_CONFIG && typeof globalThis.TRAVEL_PLAN_CONFIG === "object") {
      return globalThis.TRAVEL_PLAN_CONFIG;
    }
    if (options.configUrl === false) return {};
    const configUrl = options.configUrl || root.dataset.tripConfigUrl || "trip-data.json";
    try {
      const response = await fetch(configUrl, { cache: "no-store" });
      if (response.ok) {
        const payload = await response.json();
        return payload?.config && typeof payload.config === "object" ? payload.config : payload;
      }
    } catch {
      // A missing optional config must never prevent the local-first ledger from opening.
    }
    return {};
  }

  function resolvePersistence(root, options, config) {
    const optionPersistence = options.persistence && typeof options.persistence === "object"
      ? options.persistence
      : {};
    const configPersistence = config?.persistence && typeof config.persistence === "object"
      ? config.persistence
      : {};
    const requestedMode = options.persistenceMode
      || optionPersistence.mode
      || root.dataset.ledgerPersistence
      || configPersistence.mode;
    const sharedCollections = Array.isArray(optionPersistence.sharedCollections)
      ? optionPersistence.sharedCollections
      : Array.isArray(configPersistence.sharedCollections)
        ? configPersistence.sharedCollections
        : [];
    const d1Requested = String(requestedMode || "").trim().toLowerCase() === "d1";
    const mode = d1Requested && sharedCollections.includes("ledger") ? "d1" : "local";
    const d1Options = {
      ...(configPersistence.d1 && typeof configPersistence.d1 === "object" ? configPersistence.d1 : {}),
      ...(optionPersistence.d1 && typeof optionPersistence.d1 === "object" ? optionPersistence.d1 : {}),
      ...(options.d1 && typeof options.d1 === "object" ? options.d1 : {})
    };
    if (configPersistence.apiBase) d1Options.apiBase = configPersistence.apiBase;
    if (optionPersistence.apiBase) d1Options.apiBase = optionPersistence.apiBase;
    const localOptions = {
      ...(configPersistence.local && typeof configPersistence.local === "object" ? configPersistence.local : {}),
      ...(optionPersistence.local && typeof optionPersistence.local === "object" ? optionPersistence.local : {})
    };
    if (options.storage) localOptions.storage = options.storage;
    if (options.storageKey) localOptions.storageKey = options.storageKey;
    return { mode, d1Options, localOptions };
  }

  async function resolveTripId(root, options) {
    const explicit = options.tripId || root.dataset.tripId || document.documentElement.dataset.tripId || document.body?.dataset.tripId;
    if (explicit) return String(explicit);
    if (globalThis.TRAVEL_PLAN_DATA?.metadata?.tripId) return String(globalThis.TRAVEL_PLAN_DATA.metadata.tripId);
    try {
      const dataUrl = options.travelDataUrl || root.dataset.travelDataUrl || "trip-data.json";
      const response = await fetch(dataUrl, { cache: "no-store" });
      if (response.ok) {
        const travelData = await response.json();
        if (travelData?.metadata?.tripId) return String(travelData.metadata.tripId);
      }
    } catch {
      // A stable path-based key still keeps unrelated trips separated offline.
    }
    const pathKey = location.pathname.replace(/[^a-z0-9\u3400-\u9fff]+/gi, "-").replace(/^-|-$/g, "");
    return pathKey || "default-trip";
  }

  function travelerById(id) {
    return ledgerData.travelers.find((traveler) => traveler.id === id);
  }

  function currencyByCode(code) {
    return CURRENCY_BY_CODE.get(code) || { code, nameZh: code, nameEn: code, symbol: code };
  }

  function availableCurrencyCodes(extraCode = "") {
    return [...new Set([
      ledgerData.settings.baseCurrency,
      ...ledgerData.settings.commonCurrencies,
      extraCode
    ].filter((code) => CURRENCY_BY_CODE.has(code)))];
  }

  function billShares(bill) {
    const participantIds = bill.participantIds.filter((id) => travelerById(id));
    if (!participantIds.length) return new Map();
    const share = Math.floor(bill.baseAmountCents / participantIds.length);
    let remainder = bill.baseAmountCents - share * participantIds.length;
    return new Map(participantIds.map((id) => {
      const amount = share + (remainder > 0 ? 1 : 0);
      remainder -= remainder > 0 ? 1 : 0;
      return [id, amount];
    }));
  }

  function calculateStats() {
    const members = ledgerData.travelers.map((traveler) => ({
      traveler,
      paidCents: 0,
      owedCents: 0,
      netCents: 0,
      billIds: []
    }));
    const byId = new Map(members.map((entry) => [entry.traveler.id, entry]));
    ledgerData.bills.forEach((bill) => {
      const payer = byId.get(bill.payerId);
      if (payer) {
        payer.paidCents += bill.baseAmountCents;
        payer.billIds.push(bill.id);
      }
      billShares(bill).forEach((amount, participantId) => {
        const member = byId.get(participantId);
        if (!member) return;
        member.owedCents += amount;
        if (!member.billIds.includes(bill.id)) member.billIds.push(bill.id);
      });
    });
    members.forEach((member) => {
      member.netCents = member.paidCents - member.owedCents;
    });

    const debtors = members
      .filter((member) => member.netCents < 0)
      .map((member) => ({ id: member.traveler.id, amount: -member.netCents }))
      .sort((first, second) => second.amount - first.amount || first.id.localeCompare(second.id));
    const creditors = members
      .filter((member) => member.netCents > 0)
      .map((member) => ({ id: member.traveler.id, amount: member.netCents }))
      .sort((first, second) => second.amount - first.amount || first.id.localeCompare(second.id));
    const transferMemo = new Map();
    const settle = (debtAmounts, creditAmounts) => {
      const firstDebtor = debtAmounts.findIndex((amount) => amount > 0);
      if (firstDebtor < 0) return [];
      const memoKey = `${debtAmounts.join(",")}|${creditAmounts.join(",")}`;
      if (transferMemo.has(memoKey)) return transferMemo.get(memoKey);
      const lowerBound = Math.max(
        debtAmounts.filter((amount) => amount > 0).length,
        creditAmounts.filter((amount) => amount > 0).length
      );
      let best = null;
      const triedCreditAmounts = new Set();
      for (let creditIndex = 0; creditIndex < creditAmounts.length; creditIndex += 1) {
        const creditAmount = creditAmounts[creditIndex];
        if (creditAmount <= 0 || triedCreditAmounts.has(creditAmount)) continue;
        triedCreditAmounts.add(creditAmount);
        const amountCents = Math.min(debtAmounts[firstDebtor], creditAmount);
        const nextDebts = debtAmounts.slice();
        const nextCredits = creditAmounts.slice();
        nextDebts[firstDebtor] -= amountCents;
        nextCredits[creditIndex] -= amountCents;
        const remainder = settle(nextDebts, nextCredits);
        const candidate = [{ debtorIndex: firstDebtor, creditorIndex: creditIndex, amountCents }, ...remainder];
        if (!best || candidate.length < best.length) best = candidate;
        if (best.length === lowerBound) break;
      }
      const result = best || [];
      transferMemo.set(memoKey, result);
      return result;
    };
    const transfers = settle(
      debtors.map((debtor) => debtor.amount),
      creditors.map((creditor) => creditor.amount)
    ).map((transfer) => ({
      fromId: debtors[transfer.debtorIndex].id,
      toId: creditors[transfer.creditorIndex].id,
      amountCents: transfer.amountCents
    }));
    return {
      totalCents: ledgerData.bills.reduce((sum, bill) => sum + bill.baseAmountCents, 0),
      members,
      transfers
    };
  }

  function renderAvatar(traveler, size = "normal") {
    if (!traveler) return "";
    return `<span class="ledger-avatar ledger-avatar-${escapeAttribute(size)}" style="--ledger-avatar-color:${escapeAttribute(traveler.color)}" aria-hidden="true">${escapeHtml(traveler.initial)}</span>`;
  }

  function renderPersonChoice(traveler, type, name, selected) {
    return `
      <label class="ledger-person-choice">
        <input class="ledger-person-input" type="${type}" name="${escapeAttribute(name)}" value="${escapeAttribute(traveler.id)}" ${selected ? "checked" : ""}>
        <span class="ledger-person-visual">
          ${renderAvatar(traveler)}
          <span class="ledger-person-check" aria-hidden="true">✓</span>
        </span>
        <span class="ledger-person-name"><span data-no-translate>${escapeHtml(traveler.name)}</span></span>
      </label>`;
  }

  function renderCurrencyOptions(selectedCode) {
    return availableCurrencyCodes(selectedCode).map((code) => {
      const currency = currencyByCode(code);
      return `<button class="ledger-currency-option" type="button" data-ledger-action="choose-bill-currency" data-ledger-code="${escapeAttribute(code)}" ${code === selectedCode ? "aria-current=\"true\"" : ""}><b>${escapeHtml(code)}</b><span>${escapeHtml(currency.nameZh)}</span></button>`;
    }).join("");
  }

  function renderBillForm() {
    const editingBill = ledgerData.bills.find((bill) => bill.id === editingBillId) || null;
    const draft = editingBill ? editDraft : billDraft;
    const currency = draft?.currency || editingBill?.currency || ledgerData.settings.lastCurrency;
    const baseCurrency = ledgerData.settings.baseCurrency;
    const isForeign = currency !== baseCurrency;
    const selectedParticipants = new Set(
      draft?.participantIds
      || editingBill?.participantIds
      || ledgerData.travelers.map((traveler) => traveler.id)
    );
    const selectedPayerId = draft?.payerId || editingBill?.payerId || "";
    const selectedCategory = draft?.category || editingBill?.category || "餐饮";
    return `
      <section class="ledger-entry-card" aria-labelledby="ledger-bill-form-title">
        <div class="ledger-section-heading">
          <div>
            <p class="ledger-section-kicker">${editingBill ? "编辑账单" : "记一笔"}</p>
            <h2 id="ledger-bill-form-title">${editingBill ? "修改这笔账" : "记录本次花费"}</h2>
          </div>
          ${editingBill ? `<button class="ledger-text-button" type="button" data-ledger-action="cancel-edit">取消编辑</button>` : ""}
        </div>
        ${ledgerData.travelers.length ? `
          <form class="ledger-bill-form" data-ledger-form="bill" novalidate>
            <div class="ledger-amount-block">
              <label class="ledger-field ledger-field-currency">
                <span class="ledger-field-label">币种</span>
                <input type="hidden" name="currency" data-ledger-field="currency" value="${escapeAttribute(currency)}">
                <details class="ledger-currency-dropdown">
                  <summary><span data-ledger-currency-display>${escapeHtml(currency)} · ${escapeHtml(currencyByCode(currency).nameZh)}</span><span aria-hidden="true">⌄</span></summary>
                  <div class="ledger-currency-menu">${renderCurrencyOptions(currency)}</div>
                </details>
              </label>
              <label class="ledger-field ledger-field-amount">
                <span class="ledger-field-label">金额</span>
                <input class="ledger-amount-input" name="originalAmount" data-ledger-field="original-amount" type="text" inputmode="decimal" autocomplete="off" placeholder="0.00" value="${escapeAttribute(draft?.originalAmount ?? (editingBill ? centsToInput(editingBill.originalAmountCents) : ""))}" required>
              </label>
            </div>
            <label class="ledger-field ledger-converted-field" data-ledger-converted-field ${isForeign ? "" : "hidden"}>
              <span class="ledger-field-label">折合${escapeHtml(currencyByCode(baseCurrency).nameZh)}</span>
              <span class="ledger-converted-input-wrap">
                <span class="ledger-converted-code">${escapeHtml(baseCurrency)}</span>
                <input class="ledger-input" name="baseAmount" data-ledger-field="base-amount" type="text" inputmode="decimal" autocomplete="off" placeholder="手动填写换算后的总金额" value="${escapeAttribute(draft?.baseAmount ?? (editingBill && isForeign ? centsToInput(editingBill.baseAmountCents) : ""))}" ${isForeign ? "required" : ""}>
              </span>
              <small class="ledger-field-help">按付款当时采用的汇率手动填写</small>
            </label>

            <fieldset class="ledger-fieldset">
              <legend class="ledger-field-label">分类</legend>
              <div class="ledger-category-grid">
                ${CATEGORIES.map((category) => `
                  <label class="ledger-category-choice">
                    <input class="ledger-category-input" type="radio" name="category" value="${escapeAttribute(category)}" ${category === selectedCategory ? "checked" : ""}>
                    <span>${escapeHtml(category)}</span>
                  </label>`).join("")}
              </div>
            </fieldset>

            <label class="ledger-field ledger-note-field">
              <span class="ledger-field-label">备注 <small>选填</small></span>
              <input class="ledger-input" type="text" name="note" maxlength="160" autocomplete="off" placeholder="例如：米兰大教堂门票" value="${escapeAttribute(draft?.note ?? editingBill?.note ?? "")}">
            </label>

            <label class="ledger-field ledger-date-field">
              <span class="ledger-field-label">下单时间 <small>选填</small></span>
              <input class="ledger-input" type="datetime-local" name="orderedAt" value="${escapeAttribute(draft?.orderedAt ?? editingBill?.orderedAt ?? "")}">
            </label>

            <fieldset class="ledger-fieldset">
              <legend class="ledger-field-label">买单人 <small>单选</small></legend>
              <div class="ledger-person-grid">
                ${ledgerData.travelers.map((traveler) => renderPersonChoice(traveler, "radio", "payerId", selectedPayerId === traveler.id)).join("")}
              </div>
            </fieldset>

            <fieldset class="ledger-fieldset">
              <div class="ledger-fieldset-heading">
                <legend class="ledger-field-label">参与分账人 <small>多选</small></legend>
                <button class="ledger-text-button" type="button" data-ledger-action="select-all-participants">全选</button>
              </div>
              <div class="ledger-person-grid">
                ${ledgerData.travelers.map((traveler) => renderPersonChoice(traveler, "checkbox", "participantIds", selectedParticipants.has(traveler.id))).join("")}
              </div>
              <p class="ledger-split-summary" data-ledger-split-summary></p>
            </fieldset>

            <p class="ledger-form-error" data-ledger-form-error role="alert"></p>
            <button class="ledger-primary-button" type="submit">${editingBill ? "保存修改" : "保存账单"}</button>
          </form>` : `
          <div class="ledger-onboarding">
            <p>先添加本次同行人，再开始记账。</p>
            <button class="ledger-primary-button" type="button" data-ledger-action="open-members">添加同行人</button>
          </div>`}
      </section>`;
  }

  function formatBillDate(value) {
    if (!value) return "未填写时间";
    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) return value.replace("T", " ");
    return new Intl.DateTimeFormat(window.TravelI18n?.language || "zh-CN", {
      month: "numeric",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false
    }).format(parsed);
  }

  function renderBillNoteControl(bill, options = {}) {
    const editing = options.editing ?? editingNoteBillId === bill.id;
    const value = options.value ?? bill.note ?? "";
    return editing ? `
      <form class="ledger-bill-note-form" data-ledger-form="bill-note" data-ledger-id="${escapeAttribute(bill.id)}">
        <span>备注：</span>
        <input name="note" maxlength="160" autocomplete="off" value="${escapeAttribute(value)}" placeholder="暂无">
        <button type="submit" aria-label="保存备注">✓</button>
        <button type="button" data-ledger-action="cancel-note-edit" aria-label="取消修改备注">×</button>
      </form>` : `
      <button class="ledger-bill-note-trigger" type="button" data-ledger-action="edit-bill-note" data-ledger-id="${escapeAttribute(bill.id)}" aria-label="编辑备注：${escapeAttribute(bill.note || "暂无")}">
        <span>备注：</span><span ${bill.note ? "data-no-translate" : ""}>${escapeHtml(bill.note || "暂无")}</span>
      </button>`;
  }

  function billRowById(id) {
    return [...(ledgerRoot?.querySelectorAll("[data-ledger-bill-id]") || [])]
      .find((row) => row.dataset.ledgerBillId === id) || null;
  }

  function replaceBillNoteControl(id, editing, value) {
    const bill = ledgerData.bills.find((entry) => entry.id === id);
    const row = billRowById(id);
    const current = row?.querySelector(".ledger-bill-note-trigger, .ledger-bill-note-form");
    if (!bill || !current) return null;
    const template = document.createElement("template");
    template.innerHTML = renderBillNoteControl(bill, { editing, value }).trim();
    const replacement = template.content.firstElementChild;
    current.replaceWith(replacement);
    return replacement;
  }

  function activeBillNoteForm() {
    return editingNoteBillId
      ? ledgerRoot?.querySelector('[data-ledger-form="bill-note"]') || null
      : null;
  }

  function focusBillNoteForm(form) {
    const input = form?.querySelector('input[name="note"]');
    input?.focus({ preventScroll: true });
    input?.select();
  }

  async function flushActiveBillNote() {
    if (pendingNoteSave) return pendingNoteSave;
    const form = activeBillNoteForm();
    if (!form) {
      editingNoteBillId = null;
      return true;
    }
    return submitBillNote(form);
  }

  async function openBillNoteEditor(id) {
    const request = ++noteOpenRequest;
    const bill = ledgerData.bills.find((entry) => entry.id === id);
    if (!bill) return;
    if (editingBillId === id) {
      const fullBillNote = ledgerRoot.querySelector('[data-ledger-form="bill"] input[name="note"]');
      fullBillNote?.scrollIntoView({ behavior: "smooth", block: "center" });
      fullBillNote?.focus({ preventScroll: true });
      fullBillNote?.select();
      return;
    }
    if (editingNoteBillId === id) {
      focusBillNoteForm(activeBillNoteForm());
      return;
    }
    if (!(await flushActiveBillNote()) || request !== noteOpenRequest) return;
    editingNoteBillId = id;
    const editor = replaceBillNoteControl(id, true, bill.note || "");
    focusBillNoteForm(editor);
  }

  function cancelBillNoteEditor() {
    noteOpenRequest += 1;
    const id = editingNoteBillId;
    editingNoteBillId = null;
    if (id) replaceBillNoteControl(id, false);
  }

  function handleDocumentPointerDown(event) {
    const form = activeBillNoteForm();
    if (!form || form.contains(event.target)) return;
    const actionTarget = event.target.closest?.("[data-ledger-action]");
    if (actionTarget?.dataset.ledgerAction === "delete-bill") {
      cancelBillNoteEditor();
      return;
    }
    const nextNote = event.target.closest?.('[data-ledger-action="edit-bill-note"]');
    if (nextNote && ledgerRoot?.contains(nextNote)) return;
    void flushActiveBillNote();
  }

  function renderBillRow(bill) {
    const payer = travelerById(bill.payerId);
    const participants = bill.participantIds.map(travelerById).filter(Boolean);
    const baseCurrency = ledgerData.settings.baseCurrency;
    return `
      <article class="ledger-bill-row" data-ledger-bill-id="${escapeAttribute(bill.id)}">
        <div class="ledger-bill-main">
          <div class="ledger-bill-title-row">
            <span class="ledger-category-mark" data-ledger-category="${escapeAttribute(bill.category)}" aria-hidden="true"></span>
            <div>
              <h3>${escapeHtml(bill.category)}</h3>
              ${renderBillNoteControl(bill)}
              ${bill.orderedAt ? `<p class="ledger-bill-date">${escapeHtml(formatBillDate(bill.orderedAt))}</p>` : ""}
            </div>
          </div>
          <div class="ledger-bill-amount">
            <strong>${escapeHtml(formatMoney(bill.originalAmountCents, bill.currency))}</strong>
            ${bill.currency !== baseCurrency ? `<span>折合 ${escapeHtml(formatMoney(bill.baseAmountCents, baseCurrency))}</span>` : ""}
          </div>
        </div>
        <div class="ledger-bill-people">
          <div class="ledger-bill-payer">
            <span>买单</span>
            ${renderAvatar(payer, "small")}
            <b><span data-no-translate>${escapeHtml(payer?.name || "")}</span></b>
          </div>
          <div class="ledger-bill-participants" aria-label="参与分账：${escapeAttribute(participants.map((person) => person.name).join("、"))}">
            <span>分账</span>
            <span class="ledger-avatar-stack">${participants.map((person) => renderAvatar(person, "tiny")).join("")}</span>
            <b>${participants.length} 人</b>
          </div>
        </div>
        <div class="ledger-row-actions">
          <button class="ledger-text-button" type="button" data-ledger-action="edit-bill" data-ledger-id="${escapeAttribute(bill.id)}">编辑账单</button>
          <button class="ledger-text-button ledger-danger-button" type="button" data-ledger-action="delete-bill" data-ledger-id="${escapeAttribute(bill.id)}">删除</button>
        </div>
      </article>`;
  }

  function renderBillList() {
    const baseCurrency = ledgerData.settings.baseCurrency;
    const totalCents = ledgerData.bills.reduce((sum, bill) => sum + bill.baseAmountCents, 0);
    const bills = [...ledgerData.bills].sort((first, second) => {
      const firstDate = first.orderedAt || first.createdAt;
      const secondDate = second.orderedAt || second.createdAt;
      return secondDate.localeCompare(firstDate);
    });
    return `
      <section class="ledger-list-section" aria-labelledby="ledger-list-title">
        <div class="ledger-section-heading ledger-list-heading">
          <div>
            <p class="ledger-section-kicker">账单明细</p>
            <h2 id="ledger-list-title">${bills.length ? `${bills.length} 笔账单` : "还没有账单"}</h2>
          </div>
          <div class="ledger-list-total">
            <span>总支出</span>
            <strong>${escapeHtml(formatMoney(totalCents, baseCurrency))}</strong>
          </div>
        </div>
        ${bills.length
          ? `<div class="ledger-bill-list">${bills.map(renderBillRow).join("")}</div>`
          : `<div class="ledger-empty-state"><p>记下第一笔花费后，账单会显示在这里。</p></div>`}
      </section>`;
  }

  function renderEntryPage() {
    return `
      <section class="ledger-tab-panel" data-ledger-panel="entry" role="tabpanel" aria-labelledby="ledger-entry-tab" ${activeTab === "entry" ? "" : "hidden"}>
        <section class="ledger-members-strip" aria-label="本次同行人">
          <div class="ledger-members-strip-heading">
            <div><strong>同行人</strong><span>${ledgerData.travelers.length} 人</span></div>
            <button class="ledger-text-button" type="button" data-ledger-action="open-members">管理</button>
          </div>
          <div class="ledger-members-inline">
            ${ledgerData.travelers.map((traveler) => `<div class="ledger-person-static">${renderAvatar(traveler)}<span><span data-no-translate>${escapeHtml(traveler.name)}</span></span></div>`).join("")}
            <button class="ledger-add-person" type="button" data-ledger-action="open-members" aria-label="添加同行人"><span aria-hidden="true">＋</span><small>添加</small></button>
          </div>
        </section>
        ${renderBillForm()}
        ${renderBillList()}
      </section>`;
  }

  function renderRelatedBills(member) {
    if (!member.billIds.length) return `<p class="ledger-member-empty">暂无相关账单</p>`;
    return member.billIds.map((billId) => {
      const bill = ledgerData.bills.find((entry) => entry.id === billId);
      if (!bill) return "";
      const share = billShares(bill).get(member.traveler.id) || 0;
      return `
        <div class="ledger-member-bill">
          <span>${escapeHtml(bill.category)}${bill.payerId === member.traveler.id ? " · 买单" : ""}</span>
          <span>${share ? `分摊 ${escapeHtml(formatMoney(share, ledgerData.settings.baseCurrency))}` : "未参与分摊"}</span>
        </div>`;
    }).join("");
  }

  function renderStatsPage() {
    const stats = calculateStats();
    const baseCurrency = ledgerData.settings.baseCurrency;
    return `
      <section class="ledger-tab-panel" data-ledger-panel="stats" role="tabpanel" aria-labelledby="ledger-stats-tab" ${activeTab === "stats" ? "" : "hidden"}>
        <section class="ledger-stats-overview" aria-labelledby="ledger-stats-title">
          <p class="ledger-section-kicker">账单结算</p>
          <h2 id="ledger-stats-title">${escapeHtml(formatMoney(stats.totalCents, baseCurrency))}</h2>
          <span>${ledgerData.bills.length} 笔账单 · 以 ${escapeHtml(baseCurrency)} 结算</span>
        </section>

        <section class="ledger-settlement-section" aria-labelledby="ledger-settlement-title">
          <div class="ledger-section-heading">
            <div>
              <p class="ledger-section-kicker">结算方案</p>
              <h2 id="ledger-settlement-title">谁需要转给谁</h2>
            </div>
            <span class="ledger-soft-count">${stats.transfers.length} 笔转账</span>
          </div>
          ${stats.transfers.length ? `
            <div class="ledger-transfer-list">
              ${stats.transfers.map((transfer) => {
                const from = travelerById(transfer.fromId);
                const to = travelerById(transfer.toId);
                return `
                  <div class="ledger-transfer-row">
                    <div class="ledger-transfer-person">
                      ${renderAvatar(from)}
                      <span><strong><span data-no-translate>${escapeHtml(from?.name || "")}</span></strong><small>转给 <span data-no-translate>${escapeHtml(to?.name || "")}</span></small></span>
                    </div>
                    <strong class="ledger-transfer-amount">${escapeHtml(formatMoney(transfer.amountCents, baseCurrency))}</strong>
                  </div>`;
              }).join("")}
            </div>` : `
            <div class="ledger-empty-state"><p>${ledgerData.bills.length ? "大家已经结清，无需转账。" : "添加账单后，这里会自动生成结算单。"}</p></div>`}
        </section>

        <section class="ledger-member-stats-section" aria-labelledby="ledger-member-stats-title">
          <div class="ledger-section-heading">
            <div>
              <p class="ledger-section-kicker">成员消费明细</p>
              <h2 id="ledger-member-stats-title">每个人的收支</h2>
            </div>
          </div>
          ${stats.members.length ? `
            <div class="ledger-member-stats-list">
              ${stats.members.map((member) => `
                <details class="ledger-member-stat" open>
                  <summary class="ledger-member-stat-summary">
                    <span class="ledger-member-identity">${renderAvatar(member.traveler)}<strong><span data-no-translate>${escapeHtml(member.traveler.name)}</span></strong></span>
                    <span class="ledger-member-chevron" aria-hidden="true">›</span>
                  </summary>
                  <div class="ledger-member-stat-body">
                    <dl class="ledger-member-metrics">
                      <div><dt>实际支付</dt><dd>${escapeHtml(formatMoney(member.paidCents, baseCurrency))}</dd></div>
                      <div><dt>个人应分摊</dt><dd>${escapeHtml(formatMoney(member.owedCents, baseCurrency))}</dd></div>
                      <div><dt>结算结果</dt><dd class="${member.netCents > 0 ? "ledger-positive" : member.netCents < 0 ? "ledger-negative" : "ledger-neutral"}">${member.netCents > 0 ? "应收 " : member.netCents < 0 ? "应付 " : "已结清 "}${member.netCents === 0 ? "" : escapeHtml(formatMoney(Math.abs(member.netCents), baseCurrency))}</dd></div>
                    </dl>
                    <div class="ledger-member-bills">${renderRelatedBills(member)}</div>
                  </div>
                </details>`).join("")}
            </div>` : `<div class="ledger-empty-state"><p>添加同行人后，这里会显示每个人的收支。</p></div>`}
        </section>
      </section>`;
  }

  function renderMemberEditRow(traveler) {
    if (editingMemberId === traveler.id) {
      return `
        <form class="ledger-member-edit-row ledger-member-edit-row-is-open" data-ledger-form="member-edit" data-ledger-id="${escapeAttribute(traveler.id)}">
          ${renderAvatar(traveler)}
          <label class="ledger-visually-hidden" for="ledger-name-${escapeAttribute(traveler.id)}">成员姓名</label>
          <input class="ledger-input" id="ledger-name-${escapeAttribute(traveler.id)}" name="name" maxlength="30" value="${escapeAttribute(traveler.name)}" required>
          <label class="ledger-color-picker" title="修改头像颜色">
            <span class="ledger-visually-hidden">头像颜色</span>
            <input type="color" name="color" value="${escapeAttribute(traveler.color)}">
          </label>
          <button class="ledger-text-button" type="submit">完成</button>
          <button class="ledger-icon-button ledger-danger-button" type="button" data-ledger-action="delete-member" data-ledger-id="${escapeAttribute(traveler.id)}" aria-label="删除 ${escapeAttribute(traveler.name)}">删除</button>
        </form>`;
    }
    return `
      <div class="ledger-member-edit-row ledger-member-edit-row-static">
        ${renderAvatar(traveler)}
        <strong><span data-no-translate>${escapeHtml(traveler.name)}</span></strong>
        <span class="ledger-member-edit-actions">
          <button class="ledger-text-button" type="button" data-ledger-action="edit-member" data-ledger-id="${escapeAttribute(traveler.id)}">编辑</button>
          <button class="ledger-icon-button ledger-danger-button" type="button" data-ledger-action="delete-member" data-ledger-id="${escapeAttribute(traveler.id)}" aria-label="删除 ${escapeAttribute(traveler.name)}">删除</button>
        </span>
      </div>`;
  }

  function renderMembersDialog() {
    const suggestedColor = nextAvatarColor(ledgerData.travelers);
    return `
      <dialog class="ledger-dialog ledger-members-dialog" data-ledger-dialog="members" aria-labelledby="ledger-members-dialog-title">
        <div class="ledger-dialog-header">
          <div>
            <p class="ledger-section-kicker">同行人</p>
            <h2 id="ledger-members-dialog-title">管理本次成员</h2>
          </div>
          <button class="ledger-dialog-close" type="button" data-ledger-action="close-dialog" aria-label="关闭">×</button>
        </div>
        <div class="ledger-dialog-body">
          ${ledgerData.travelers.length ? `
            <div class="ledger-member-edit-list">
              ${ledgerData.travelers.map(renderMemberEditRow).join("")}
            </div>` : `<p class="ledger-dialog-empty">还没有同行人。</p>`}
          <form class="ledger-add-member-form" data-ledger-form="member-add">
            <div class="ledger-add-member-preview" data-ledger-member-preview style="--ledger-avatar-color:${escapeAttribute(suggestedColor)}">?</div>
            <label class="ledger-field ledger-add-member-name">
              <span class="ledger-field-label">添加成员</span>
              <input class="ledger-input" name="name" maxlength="30" placeholder="输入姓名" autocomplete="off" required>
            </label>
            <label class="ledger-color-picker" title="选择头像颜色">
              <span class="ledger-visually-hidden">头像颜色</span>
              <input type="color" name="color" value="${escapeAttribute(suggestedColor)}">
            </label>
            <button class="ledger-secondary-button" type="submit">添加</button>
          </form>
          <p class="ledger-dialog-note">头像文字会从姓名自动提取；颜色可以随时修改。</p>
        </div>
      </dialog>`;
  }

  function renderCurrencyChip(code) {
    const currency = currencyByCode(code);
    return `
      <span class="ledger-currency-chip">
        <b>${escapeHtml(code)}</b>
        <span>${escapeHtml(currency.nameZh)}</span>
        <button type="button" data-ledger-action="remove-common-currency" data-ledger-code="${escapeAttribute(code)}" aria-label="移除 ${escapeAttribute(currency.nameZh)}">×</button>
      </span>`;
  }

  function renderSettingsDialog() {
    const baseCurrency = currencyByCode(ledgerData.settings.baseCurrency);
    const baseLocked = ledgerData.bills.length > 0;
    return `
      <dialog class="ledger-dialog ledger-settings-dialog" data-ledger-dialog="settings" aria-labelledby="ledger-settings-dialog-title">
        <div class="ledger-dialog-header">
          <div>
            <p class="ledger-section-kicker">记账设置</p>
            <h2 id="ledger-settings-dialog-title">货币</h2>
          </div>
          <button class="ledger-dialog-close" type="button" data-ledger-action="close-dialog" aria-label="关闭">×</button>
        </div>
        <div class="ledger-dialog-body">
          <section class="ledger-setting-group">
            <div class="ledger-setting-heading">
              <div><h3>记账本位币</h3><p>统计与最终结算都使用这个币种</p></div>
            </div>
            <button class="ledger-currency-select-button" type="button" data-ledger-action="pick-base-currency" ${baseLocked ? "disabled" : ""}>
              <span class="ledger-currency-symbol">${escapeHtml(baseCurrency.symbol)}</span>
              <span><strong>${escapeHtml(baseCurrency.code)} · ${escapeHtml(baseCurrency.nameZh)}</strong><small>${escapeHtml(baseCurrency.nameEn)}</small></span>
              <span aria-hidden="true">›</span>
            </button>
            ${baseLocked ? `<p class="ledger-setting-note">已有账单后，本位币会锁定，避免历史换算金额失真。</p>` : ""}
          </section>
          <section class="ledger-setting-group">
            <div class="ledger-setting-heading">
              <div><h3>常用外币</h3><p>只在记账时显示你选中的币种</p></div>
              <button class="ledger-text-button" type="button" data-ledger-action="pick-common-currency">添加货币</button>
            </div>
            ${ledgerData.settings.commonCurrencies.length
              ? `<div class="ledger-currency-chips">${ledgerData.settings.commonCurrencies.map(renderCurrencyChip).join("")}</div>`
              : `<p class="ledger-dialog-empty">尚未添加常用外币。</p>`}
          </section>
        </div>
      </dialog>`;
  }

  function searchedCurrencies() {
    const query = normalizeSearch(currencyQuery);
    if (!query) return [];
    return CURRENCY_CATALOG
      .filter((currency) => currencySearchText.get(currency.code).includes(query))
      .slice(0, 24);
  }

  function currencyResultMarkup(currency) {
    const isBase = currency.code === ledgerData.settings.baseCurrency;
    const isSelected = currencyPickerMode === "base"
      ? isBase
      : ledgerData.settings.commonCurrencies.includes(currency.code);
    const disabled = currencyPickerMode === "common" && isBase;
    return `
      <button class="ledger-currency-result ${isSelected ? "ledger-is-selected" : ""}" type="button" data-ledger-action="choose-currency" data-ledger-code="${escapeAttribute(currency.code)}" ${disabled ? "disabled" : ""}>
        <span class="ledger-currency-symbol">${escapeHtml(currency.symbol)}</span>
        <span class="ledger-currency-result-name"><strong>${escapeHtml(currency.code)} · ${escapeHtml(currency.nameZh)}</strong><small>${escapeHtml(currency.nameEn)}</small></span>
        <span class="ledger-currency-result-state">${disabled ? "本位币" : isSelected ? "已选择" : "选择"}</span>
      </button>`;
  }

  function renderCurrencyResultsMarkup() {
    const currencies = searchedCurrencies();
    if (!normalizeSearch(currencyQuery)) {
      return `<div class="ledger-currency-empty"><p>输入货币名称开始查找</p><small>例如：港币、Hong Kong 或 HKD</small></div>`;
    }
    return currencies.length
      ? currencies.map(currencyResultMarkup).join("")
      : `<div class="ledger-currency-empty"><p>没有找到相关货币</p><small>可以尝试中文名、英文名、代码、符号或国家与地区。</small></div>`;
  }

  function renderCurrencyDialog() {
    return `
      <dialog class="ledger-dialog ledger-currency-dialog" data-ledger-dialog="currency" aria-labelledby="ledger-currency-dialog-title">
        <div class="ledger-dialog-header">
          <div>
            <p class="ledger-section-kicker">世界货币</p>
            <h2 id="ledger-currency-dialog-title">${currencyPickerMode === "base" ? "选择本位币" : "添加常用外币"}</h2>
          </div>
          <button class="ledger-dialog-close" type="button" data-ledger-action="back-to-settings" aria-label="返回设置">×</button>
        </div>
        <div class="ledger-dialog-body">
          <label class="ledger-currency-search">
            <span class="ledger-visually-hidden">搜索货币</span>
            <span aria-hidden="true">⌕</span>
            <input class="ledger-input" type="search" data-ledger-currency-search placeholder="搜索港币、Hong Kong、HKD…" value="${escapeAttribute(currencyQuery)}" autocomplete="off">
          </label>
          <p class="ledger-search-help">支持中文名、英文名、代码、符号和国家或地区</p>
          <div class="ledger-currency-results" data-ledger-currency-results>${renderCurrencyResultsMarkup()}</div>
        </div>
      </dialog>`;
  }

  function renderApp() {
    if (!ledgerRoot || !ledgerData) return;
    ledgerRoot.innerHTML = `
      <div class="ledger-app" data-ledger-trip-id="${escapeAttribute(ledgerTripId)}">
        <header class="ledger-page-header">
          <h1>旅行记账</h1>
          <div class="ledger-header-actions">
            <button class="ledger-icon-button" type="button" data-ledger-action="open-settings" aria-label="记账设置">设置</button>
          </div>
        </header>
        <nav class="ledger-tabs" role="tablist" aria-label="记账页面">
          <button id="ledger-entry-tab" class="ledger-tab ${activeTab === "entry" ? "ledger-is-active" : ""}" type="button" role="tab" aria-selected="${activeTab === "entry"}" data-ledger-action="set-tab" data-ledger-tab="entry">记账</button>
          <button id="ledger-stats-tab" class="ledger-tab ${activeTab === "stats" ? "ledger-is-active" : ""}" type="button" role="tab" aria-selected="${activeTab === "stats"}" data-ledger-action="set-tab" data-ledger-tab="stats">账单结算</button>
        </nav>
        <div class="ledger-live" role="status" aria-live="polite">${escapeHtml(notice)}</div>
        ${renderEntryPage()}
        ${renderStatsPage()}
        ${renderMembersDialog()}
        ${renderSettingsDialog()}
        ${renderCurrencyDialog()}
      </div>`;
    syncSplitSummary();
    attachDialogBehavior();
    if (openDialogName) {
      const dialog = ledgerRoot.querySelector(`[data-ledger-dialog="${openDialogName}"]`);
      if (dialog) {
        if (typeof dialog.showModal === "function") dialog.showModal();
        else dialog.setAttribute("open", "");
        if (openDialogName === "currency") {
          const search = dialog.querySelector("[data-ledger-currency-search]");
          if (search) {
            search.focus({ preventScroll: true });
            search.setSelectionRange(search.value.length, search.value.length);
          }
        }
      }
    }
  }

  function setNotice(message) {
    notice = message;
    const live = ledgerRoot?.querySelector(".ledger-live");
    if (live) live.textContent = message;
  }

  function setFormError(form, message) {
    const target = form.querySelector("[data-ledger-form-error]");
    if (target) target.textContent = message;
    const live = ledgerRoot?.querySelector(".ledger-live");
    if (live) live.textContent = message;
  }

  function enqueueMutation(operation) {
    const queued = mutationQueue.then(operation, operation);
    mutationQueue = queued.catch(() => {});
    return queued;
  }

  async function mutateData(mutator, options = {}) {
    return enqueueMutation(async () => {
      const next = deepClone(ledgerData);
      const generation = draftGeneration;
      const alreadyPending = ledgerAdapter.pending;
      mutator(next);
      next.version = STORAGE_VERSION;
      next.updatedAt = new Date().toISOString();
      try {
        await Promise.resolve(ledgerAdapter.save(next, { tripId: ledgerTripId }));
        ledgerData = normalizeData(next);
        if (typeof options.afterSuccess === "function") options.afterSuccess();
        notice = options.message || "";
        renderApp();
        ledgerRoot.dispatchEvent(new CustomEvent("travel-ledger:changed", {
          bubbles: true,
          detail: { tripId: ledgerTripId, reason: options.reason || "update", data: deepClone(ledgerData) }
        }));
        return true;
      } catch (error) {
        if (ledgerAdapter.pending && !alreadyPending) recoveredMutation = {generation, afterSuccess: options.afterSuccess};
        if (error.status === 409) {
          // Rebase the observed revision without replacing the active form. The next
          // user save applies their retained fields to the fresh server snapshot.
          try { ledgerData = normalizeData(await ledgerAdapter.load()); renderDirty = true; } catch {}
        }
        console.error("TravelLedger could not save data", error);
        setNotice(ledgerPersistenceMode === "d1"
          ? error.message
          : "本地保存失败，请检查浏览器存储空间或隐私设置后重试。");
        return false;
      }
    });
  }

  function captureBillDraft() {
    if (!ledgerRoot) return;
    const form = ledgerRoot.querySelector('[data-ledger-form="bill"]');
    if (!form) return;
    const formData = new FormData(form);
    const draft = {
      currency: String(formData.get("currency") || ledgerData.settings.lastCurrency),
      originalAmount: String(formData.get("originalAmount") || ""),
      baseAmount: String(formData.get("baseAmount") || ""),
      category: String(formData.get("category") || "餐饮"),
      note: String(formData.get("note") || "").trim().slice(0, 160),
      orderedAt: String(formData.get("orderedAt") || ""),
      payerId: String(formData.get("payerId") || ""),
      participantIds: formData.getAll("participantIds").map(String)
    };
    if (editingBillId) editDraft = draft; else billDraft = draft;
  }

  function syncSplitSummary() {
    if (!ledgerRoot || !ledgerData) return;
    const form = ledgerRoot.querySelector('[data-ledger-form="bill"]');
    const summary = form?.querySelector("[data-ledger-split-summary]");
    if (!form || !summary) return;
    const participants = [...form.querySelectorAll('input[name="participantIds"]:checked')];
    if (!participants.length) {
      summary.textContent = "请选择至少一位分账人";
      return;
    }
    const currency = form.elements.currency?.value || ledgerData.settings.baseCurrency;
    const amountField = currency === ledgerData.settings.baseCurrency
      ? form.elements.originalAmount
      : form.elements.baseAmount;
    const amountCents = toCents(amountField?.value);
    if (!amountCents || amountCents <= 0) {
      summary.textContent = `已选 ${participants.length} 人 · 按人数平分`;
      return;
    }
    const averageCents = Math.floor(amountCents / participants.length);
    summary.textContent = `已选 ${participants.length} 人 · 每人约 ${formatMoney(averageCents, ledgerData.settings.baseCurrency)}`;
  }

  function syncCurrencyField(select) {
    const form = select.closest("form");
    if (!form) return;
    const convertedField = form.querySelector("[data-ledger-converted-field]");
    const convertedInput = form.querySelector('[data-ledger-field="base-amount"]');
    const isForeign = select.value !== ledgerData.settings.baseCurrency;
    if (convertedField) convertedField.hidden = !isForeign;
    if (convertedInput) {
      convertedInput.required = isForeign;
      if (!isForeign) convertedInput.value = "";
    }
    captureBillDraft();
    syncSplitSummary();
  }

  function syncMemberPreview(form) {
    const preview = form.querySelector("[data-ledger-member-preview]");
    if (!preview) return;
    const name = form.elements.name?.value || "";
    const color = form.elements.color?.value || nextAvatarColor(ledgerData.travelers);
    preview.textContent = name.trim() ? avatarInitial(name) : "?";
    if (isValidColor(color)) preview.style.setProperty("--ledger-avatar-color", color);
  }

  function attachDialogBehavior() {
    ledgerRoot.querySelectorAll("dialog[data-ledger-dialog]").forEach((dialog) => {
      dialog.addEventListener("close", () => {
        if (dialog.dataset.ledgerDialog === "members") editingMemberId = null;
        if (openDialogName === dialog.dataset.ledgerDialog) openDialogName = null;
      });
      dialog.addEventListener("cancel", () => {
        openDialogName = null;
      });
      dialog.addEventListener("click", (event) => {
        if (event.target === dialog) closeDialog(dialog);
      });
    });
  }

  function showDialog(name, { focusSearch = false } = {}) {
    if (!ledgerRoot) return;
    const dialog = ledgerRoot.querySelector(`[data-ledger-dialog="${name}"]`);
    if (!dialog) return;
    const current = ledgerRoot.querySelector("dialog[open]");
    if (current && current !== dialog) {
      openDialogName = null;
      if (typeof current.close === "function") current.close();
      else current.removeAttribute("open");
    }
    openDialogName = name;
    if (!dialog.open) {
      if (typeof dialog.showModal === "function") dialog.showModal();
      else dialog.setAttribute("open", "");
    }
    const focusTarget = focusSearch
      ? dialog.querySelector("[data-ledger-currency-search]")
      : dialog.querySelector("input:not([type=color]), button");
    requestAnimationFrame(() => focusTarget?.focus({ preventScroll: true }));
  }

  function closeDialog(dialog = ledgerRoot?.querySelector("dialog[open]")) {
    if (!dialog) {
      openDialogName = null;
      return;
    }
    if (dialog.dataset.ledgerDialog === "members") editingMemberId = null;
    openDialogName = null;
    if (typeof dialog.close === "function") dialog.close();
    else dialog.removeAttribute("open");
  }

  function updateCurrencyDialog(mode) {
    currencyPickerMode = mode;
    currencyQuery = "";
    const dialog = ledgerRoot.querySelector('[data-ledger-dialog="currency"]');
    if (!dialog) return;
    const title = dialog.querySelector("#ledger-currency-dialog-title");
    const search = dialog.querySelector("[data-ledger-currency-search]");
    const results = dialog.querySelector("[data-ledger-currency-results]");
    if (title) title.textContent = mode === "base" ? "选择本位币" : "添加常用外币";
    if (search) search.value = "";
    if (results) results.innerHTML = renderCurrencyResultsMarkup();
    showDialog("currency", { focusSearch: true });
  }

  function chooseBillCurrency(button) {
    const form = button.closest('[data-ledger-form="bill"]');
    const code = button.dataset.ledgerCode || "";
    if (!form || !availableCurrencyCodes(code).includes(code)) return;
    const field = form.querySelector('[data-ledger-field="currency"]');
    const display = form.querySelector("[data-ledger-currency-display]");
    const dropdown = button.closest("details");
    if (field) field.value = code;
    if (display) display.textContent = `${code} · ${currencyByCode(code).nameZh}`;
    dropdown?.removeAttribute("open");
    if (field) syncCurrencyField(field);
  }

  function isDuplicateTravelerName(name, ignoredId = "") {
    const normalized = name.trim().toLocaleLowerCase();
    return ledgerData.travelers.some((traveler) => (
      traveler.id !== ignoredId && traveler.name.trim().toLocaleLowerCase() === normalized
    ));
  }

  async function submitBill(form) {
    const formData = new FormData(form);
    const currency = String(formData.get("currency") || "").toUpperCase();
    const originalAmountCents = toCents(formData.get("originalAmount"));
    const isForeign = currency !== ledgerData.settings.baseCurrency;
    const baseAmountCents = isForeign ? toCents(formData.get("baseAmount")) : originalAmountCents;
    const category = String(formData.get("category") || "");
    const payerId = String(formData.get("payerId") || "");
    const participantIds = [...new Set(formData.getAll("participantIds").map(String))]
      .filter((id) => travelerById(id));

    if (!availableCurrencyCodes(currency).includes(currency)) {
      setFormError(form, "请选择本次旅程使用的币种。");
      return;
    }
    if (!originalAmountCents || originalAmountCents <= 0) {
      setFormError(form, "请输入正确的账单金额，最多保留两位小数。");
      form.elements.originalAmount?.focus();
      return;
    }
    if (!baseAmountCents || baseAmountCents <= 0) {
      setFormError(form, `请填写折合${currencyByCode(ledgerData.settings.baseCurrency).nameZh}的金额。`);
      form.elements.baseAmount?.focus();
      return;
    }
    if (!CATEGORIES.includes(category)) {
      setFormError(form, "请选择账单分类。");
      return;
    }
    if (!travelerById(payerId)) {
      setFormError(form, "请选择一位买单人。");
      return;
    }
    if (!participantIds.length) {
      setFormError(form, "请选择至少一位参与分账的人。");
      return;
    }

    const now = new Date().toISOString();
    const fields = {
      originalAmountCents,
      baseAmountCents,
      currency,
      category,
      note: String(formData.get("note") || "").trim().slice(0, 160),
      orderedAt: String(formData.get("orderedAt") || ""),
      payerId,
      participantIds,
      updatedAt: now
    };
    const billBeingEdited = ledgerData.bills.find((bill) => bill.id === editingBillId);
    if (editingBillId && !billBeingEdited) { setNotice("这笔账单已被同行者删除；你的表单仍保留，请取消编辑后决定是否另建账单。"); return; }
    await mutateData((next) => {
      if (billBeingEdited) {
        const index = next.bills.findIndex((bill) => bill.id === billBeingEdited.id);
        if (index >= 0) next.bills[index] = { ...next.bills[index], ...fields };
      } else {
        next.bills.push({ id: makeId("bill"), ...fields, createdAt: now });
        next.settings.lastCurrency = currency;
      }
    }, {
      reason: billBeingEdited ? "bill-updated" : "bill-added",
      message: billBeingEdited ? "账单已更新" : "账单已保存",
      afterSuccess() {
        editingBillId = null;
        billDraft = null;
        editDraft = null;
      }
    });
  }

  async function submitMemberAdd(form) {
    const name = String(new FormData(form).get("name") || "").trim();
    const color = String(new FormData(form).get("color") || "").toUpperCase();
    if (!name) {
      form.elements.name?.focus();
      setNotice("请输入同行人的姓名。");
      return;
    }
    if (isDuplicateTravelerName(name)) {
      form.elements.name?.focus();
      setNotice("这位同行人已经添加过了。");
      return;
    }
    const id = makeId("person");
    const traveler = {
      id,
      name: name.slice(0, 30),
      initial: avatarInitial(name),
      color: isValidColor(color) ? color : nextAvatarColor(ledgerData.travelers)
    };
    captureBillDraft();
    if (billDraft) billDraft.participantIds = [...new Set([...billDraft.participantIds, id])];
    openDialogName = "members";
    await mutateData((next) => next.travelers.push(traveler), {
      reason: "member-added",
      message: `${traveler.name}已加入同行人`
    });
  }

  async function submitBillNote(form) {
    const id = form.dataset.ledgerId || "";
    const bill = ledgerData.bills.find((entry) => entry.id === id);
    if (!bill) return false;
    const note = String(new FormData(form).get("note") || "").trim().slice(0, 160);
    if (note === (bill.note || "")) {
      if (editingNoteBillId === id) editingNoteBillId = null;
      replaceBillNoteControl(id, false);
      return true;
    }
    if (pendingNoteSave) return pendingNoteSave;
    form.classList.add("ledger-is-saving");
    for (const control of form.elements) control.disabled = true;
    const operation = enqueueMutation(async () => {
      try {
        const latestBill = ledgerData.bills.find((entry) => entry.id === id);
        if (!latestBill) return false;
        if (note === (latestBill.note || "")) {
          if (editingNoteBillId === id) editingNoteBillId = null;
          replaceBillNoteControl(id, false);
          return true;
        }
        const now = new Date().toISOString();
        const next = deepClone(ledgerData);
        const target = next.bills.find((entry) => entry.id === id);
        if (!target) return false;
        target.note = note;
        target.updatedAt = now;
        next.version = STORAGE_VERSION;
        next.updatedAt = now;
        await Promise.resolve(ledgerAdapter.save(next, { tripId: ledgerTripId }));
        ledgerData = normalizeData(next);
        if (editingNoteBillId === id) editingNoteBillId = null;
        const fullBillNote = editingBillId === id
          ? ledgerRoot.querySelector('[data-ledger-form="bill"] input[name="note"]')
          : null;
        if (fullBillNote) fullBillNote.value = note;
        replaceBillNoteControl(id, false);
        setNotice(note ? "备注已更新" : "备注已清空");
        ledgerRoot.dispatchEvent(new CustomEvent("travel-ledger:changed", {
          bubbles: true,
          detail: { tripId: ledgerTripId, reason: "bill-note-updated", data: deepClone(ledgerData) }
        }));
        return true;
      } catch (error) {
        console.error("TravelLedger could not save note", error);
        form.classList.remove("ledger-is-saving");
        for (const control of form.elements) control.disabled = false;
        setNotice(ledgerPersistenceMode === "d1"
          ? "备注保存失败，请检查网络或你的云端数据库配置后重试。"
          : "备注本地保存失败，请检查浏览器存储空间或隐私设置后重试。");
        return false;
      }
    });
    pendingNoteSave = operation;
    operation.then(
      () => { if (pendingNoteSave === operation) pendingNoteSave = null; },
      () => { if (pendingNoteSave === operation) pendingNoteSave = null; }
    );
    return operation;
  }

  async function submitMemberEdit(form) {
    const id = form.dataset.ledgerId || "";
    const formData = new FormData(form);
    const name = String(formData.get("name") || "").trim();
    const color = String(formData.get("color") || "").toUpperCase();
    if (!name) {
      form.elements.name?.focus();
      setNotice("姓名不能为空。");
      return;
    }
    if (isDuplicateTravelerName(name, id)) {
      form.elements.name?.focus();
      setNotice("已有同名的同行人，请换一个称呼。");
      return;
    }
    captureBillDraft();
    openDialogName = "members";
    await mutateData((next) => {
      const traveler = next.travelers.find((entry) => entry.id === id);
      if (!traveler) return;
      traveler.name = name.slice(0, 30);
      traveler.initial = avatarInitial(name);
      if (isValidColor(color)) traveler.color = color;
    }, { reason: "member-updated", message: "同行人信息已更新", afterSuccess() { editingMemberId = null; } });
  }

  function confirmLedgerAction(message) {
    return new Promise((resolve) => {
      const dialog = document.createElement("dialog");
      dialog.className = "ledger-confirm-dialog";
      dialog.setAttribute("aria-modal", "true");
      dialog.setAttribute("aria-label", "确认删除");
      dialog.innerHTML = `<div class="ledger-confirm-card">
        <p>${escapeHtml(message)}</p>
        <div class="ledger-confirm-actions">
          <button type="button" data-ledger-confirm="cancel">取消</button>
          <button type="button" class="ledger-confirm-danger" data-ledger-confirm="confirm">确认删除</button>
        </div>
      </div>`;
      let settled = false;
      const finish = (confirmed) => {
        if (settled) return;
        settled = true;
        if (dialog.open && typeof dialog.close === "function") dialog.close();
        dialog.remove();
        resolve(confirmed);
      };
      dialog.addEventListener("cancel", (event) => {
        event.preventDefault();
        finish(false);
      });
      dialog.addEventListener("click", (event) => {
        const choice = event.target.closest("[data-ledger-confirm]");
        if (choice) finish(choice.dataset.ledgerConfirm === "confirm");
        else if (event.target === dialog) finish(false);
      });
      document.body.append(dialog);
      if (typeof dialog.showModal === "function") dialog.showModal();
      else dialog.setAttribute("open", "");
      requestAnimationFrame(() => dialog.querySelector('[data-ledger-confirm="cancel"]')?.focus());
    });
  }

  async function deleteMember(id) {
    const traveler = travelerById(id);
    if (!traveler) return;
    const referenced = ledgerData.bills.some((bill) => (
      bill.payerId === id || bill.participantIds.includes(id)
    ));
    if (referenced) {
      setNotice(`${traveler.name}已有相关账单，需先处理这些账单后才能删除。`);
      return;
    }
    if (!await confirmLedgerAction(`删除同行人“${traveler.name}”？`)) return;
    captureBillDraft();
    if (billDraft) {
      billDraft.participantIds = billDraft.participantIds.filter((memberId) => memberId !== id);
      if (billDraft.payerId === id) billDraft.payerId = "";
    }
    editingMemberId = null;
    openDialogName = "members";
    await mutateData((next) => {
      next.travelers = next.travelers.filter((entry) => entry.id !== id);
    }, { reason: "member-deleted", message: `${traveler.name}已移除` });
  }

  async function deleteBill(id) {
    const bill = ledgerData.bills.find((entry) => entry.id === id);
    if (!bill || !await confirmLedgerAction("删除这笔账单？")) return;
    if (editingNoteBillId === id) editingNoteBillId = null;
    await mutateData((next) => {
      next.bills = next.bills.filter((entry) => entry.id !== id);
    }, { reason: "bill-deleted", message: "账单已删除" });
  }

  async function removeCommonCurrency(code) {
    if (!ledgerData.settings.commonCurrencies.includes(code)) return;
    captureBillDraft();
    openDialogName = "settings";
    await mutateData((next) => {
      next.settings.commonCurrencies = next.settings.commonCurrencies.filter((item) => item !== code);
      if (next.settings.lastCurrency === code) next.settings.lastCurrency = next.settings.baseCurrency;
    }, { reason: "currency-removed", message: `${currencyByCode(code).nameZh}已移除` });
  }

  async function chooseCurrency(code) {
    if (!CURRENCY_BY_CODE.has(code)) return;
    captureBillDraft();
    if (currencyPickerMode === "base") {
      if (ledgerData.bills.length) {
        setNotice("已有账单，本位币不能再修改。");
        return;
      }
      openDialogName = "settings";
      await mutateData((next) => {
        next.settings.baseCurrency = code;
        next.settings.commonCurrencies = next.settings.commonCurrencies.filter((item) => item !== code);
        next.settings.lastCurrency = code;
      }, { reason: "base-currency-changed", message: `本位币已设为${currencyByCode(code).nameZh}` });
      return;
    }

    const selected = ledgerData.settings.commonCurrencies.includes(code);
    openDialogName = "currency";
    await mutateData((next) => {
      next.settings.commonCurrencies = selected
        ? next.settings.commonCurrencies.filter((item) => item !== code)
        : [...next.settings.commonCurrencies, code];
      if (selected && next.settings.lastCurrency === code) next.settings.lastCurrency = next.settings.baseCurrency;
    }, {
      reason: selected ? "currency-removed" : "currency-added",
      message: selected ? `${currencyByCode(code).nameZh}已移除` : `${currencyByCode(code).nameZh}已加入常用外币`
    });
  }

  function editBill(id) {
    if (!ledgerData.bills.some((bill) => bill.id === id)) return;
    if (editingBillId && editingBillId !== id) {
      setNotice("请先保存或取消正在编辑的账单。");
      ledgerRoot.querySelector('[data-ledger-form="bill"] [data-ledger-field="original-amount"]')?.focus({ preventScroll: true });
      return;
    }
    captureBillDraft();
    editingBillId = id;
    editDraft = null;
    activeTab = "entry";
    notice = "";
    renderApp();
    requestAnimationFrame(() => {
      ledgerRoot.querySelector(".ledger-entry-card")?.scrollIntoView({ behavior: "smooth", block: "start" });
      ledgerRoot.querySelector('[data-ledger-field="original-amount"]')?.focus({ preventScroll: true });
    });
  }

  function handleAction(button) {
    const action = button.dataset.ledgerAction;
    if (!action) return;
    if (action === "set-tab") {
      captureBillDraft();
      setActiveTab(button.dataset.ledgerTab);
    } else if (action === "open-members") {
      captureBillDraft();
      showDialog("members");
    } else if (action === "open-settings") {
      captureBillDraft();
      showDialog("settings");
    } else if (action === "edit-member") {
      captureBillDraft();
      editingMemberId = button.dataset.ledgerId || null;
      openDialogName = "members";
      renderApp();
      requestAnimationFrame(() => ledgerRoot.querySelector('[data-ledger-form="member-edit"] input[name="name"]')?.focus());
    } else if (action === "close-dialog") {
      closeDialog(button.closest("dialog"));
    } else if (action === "back-to-settings") {
      closeDialog(button.closest("dialog"));
      showDialog("settings");
    } else if (action === "pick-base-currency") {
      updateCurrencyDialog("base");
    } else if (action === "pick-common-currency") {
      updateCurrencyDialog("common");
    } else if (action === "choose-bill-currency") {
      chooseBillCurrency(button);
    } else if (action === "choose-currency") {
      chooseCurrency(button.dataset.ledgerCode || "");
    } else if (action === "remove-common-currency") {
      removeCommonCurrency(button.dataset.ledgerCode || "");
    } else if (action === "delete-member") {
      deleteMember(button.dataset.ledgerId || "");
    } else if (action === "edit-bill") {
      editBill(button.dataset.ledgerId || "");
    } else if (action === "delete-bill") {
      deleteBill(button.dataset.ledgerId || "");
    } else if (action === "edit-bill-note") {
      void openBillNoteEditor(button.dataset.ledgerId || "");
    } else if (action === "cancel-note-edit") {
      cancelBillNoteEditor();
    } else if (action === "cancel-edit") {
      editingBillId = null;
      renderApp();
    } else if (action === "select-all-participants") {
      const form = button.closest("form");
      const inputs = [...form.querySelectorAll('input[name="participantIds"]')];
      const shouldSelectAll = inputs.some((input) => !input.checked);
      inputs.forEach((input) => { input.checked = shouldSelectAll; });
      captureBillDraft();
      syncSplitSummary();
    }
  }

  async function handleRootClick(event) {
    const button = event.target.closest("[data-ledger-action]");
    if (!button || !ledgerRoot.contains(button)) return;
    event.preventDefault();
    const action = button.dataset.ledgerAction;
    const insideNoteForm = button.closest('[data-ledger-form="bill-note"]');
    if (editingNoteBillId
      && !insideNoteForm
      && action !== "edit-bill-note"
      && action !== "cancel-note-edit"
      && !(await flushActiveBillNote())) return;
    handleAction(button);
  }

  function handleRootInput(event) {
    if (event.target.matches("[data-ledger-currency-search]")) {
      currencyQuery = event.target.value;
      const results = ledgerRoot.querySelector("[data-ledger-currency-results]");
      if (results) results.innerHTML = renderCurrencyResultsMarkup();
      return;
    }
    const memberForm = event.target.closest('[data-ledger-form="member-add"]');
    if (memberForm) syncMemberPreview(memberForm);
    if (event.target.closest('[data-ledger-form="bill"]')) {
      captureBillDraft();
      syncSplitSummary();
    }
  }

  function handleRootChange(event) {
    if (event.target.matches('[data-ledger-field="currency"]')) syncCurrencyField(event.target);
    if (event.target.closest('[data-ledger-form="bill"]')) {
      captureBillDraft();
      syncSplitSummary();
    }
  }

  async function handleRootSubmit(event) {
    const form = event.target.closest("form[data-ledger-form]");
    if (!form || !ledgerRoot.contains(form)) return;
    event.preventDefault();
    if (form.dataset.ledgerForm === "bill-note") {
      await submitBillNote(form);
      return;
    }
    if (editingNoteBillId && !(await flushActiveBillNote())) return;
    if (form.dataset.ledgerForm === "bill") await submitBill(form);
    if (form.dataset.ledgerForm === "member-add") await submitMemberAdd(form);
    if (form.dataset.ledgerForm === "member-edit") await submitMemberEdit(form);
  }

  function handleRootKeydown(event) {
    if (event.key === "Escape" && event.target.closest('[data-ledger-form="bill-note"]')) {
      event.preventDefault();
      cancelBillNoteEditor();
      return;
    }
    if (!event.target.matches('[role="tab"]') || !["ArrowLeft", "ArrowRight"].includes(event.key)) return;
    event.preventDefault();
    const nextTab = event.target.dataset.ledgerTab === "entry" ? "stats" : "entry";
    setActiveTab(nextTab);
    requestAnimationFrame(() => ledgerRoot.querySelector(`[data-ledger-tab="${nextTab}"]`)?.focus());
  }

  function setActiveTab(tab, options = {}) {
    const nextTab = tab === "stats" ? "stats" : "entry";
    if (editingNoteBillId && !options.skipNoteFlush) {
      void flushActiveBillNote().then((saved) => {
        if (saved) setActiveTab(nextTab, { ...options, skipNoteFlush: true });
      });
      return;
    }
    const changed = activeTab !== nextTab;
    if (changed) captureBillDraft();
    activeTab = nextTab;
    if (ledgerData && (changed || options.forceRender)) renderApp();
    if (options.updateHash !== false && changed) {
      window.dispatchEvent(new CustomEvent("travel-ledger:navigate", { detail: { tab: nextTab } }));
    }
  }

  async function init(options = {}) {
    const requestedRoot = typeof options.root === "string"
      ? document.querySelector(options.root)
      : options.root || document.querySelector("#ledger-root");
    if (!requestedRoot) return null;
    if (initialized && requestedRoot === ledgerRoot) return deepClone(ledgerData);

    ledgerRoot = requestedRoot;
    ledgerRoot.setAttribute("aria-busy", "true");
    const [resolvedTripId, tripConfig] = await Promise.all([
      resolveTripId(ledgerRoot, options),
      resolveTripConfig(ledgerRoot, options)
    ]);
    ledgerTripId = resolvedTripId;
    const persistence = resolvePersistence(ledgerRoot, options, tripConfig);
    ledgerAdapter = options.repository || options.adapter || (persistence.mode === "d1"
      ? createD1Adapter(ledgerTripId, persistence.d1Options)
      : createLocalStorageAdapter(ledgerTripId, persistence.localOptions));
    ledgerPersistenceMode = options.repository || options.adapter
      ? String(ledgerAdapter.mode || "custom")
      : persistence.mode;
    let stored = null;
    try {
      stored = await Promise.resolve(ledgerAdapter.load({ tripId: ledgerTripId }));
    } catch (error) {
      console.error("TravelLedger could not load data", error);
      notice = ledgerPersistenceMode === "d1"
        ? "共享账本尚未读取成功，请刷新共享数据。当前空白不代表云端没有账单。"
        : "本地账本暂时无法读取，已打开一份空账本。";
    }
    ledgerData = normalizeData(stored);
    activeTab = location.hash === "#ledger-stats" ? "stats" : "entry";
    ledgerRoot.addEventListener("click", handleRootClick);
    ledgerRoot.addEventListener("input", handleRootInput);
    ledgerRoot.addEventListener("input", () => { draftGeneration += 1; });
    ledgerRoot.addEventListener("change", () => { draftGeneration += 1; });
    ledgerRoot.addEventListener("change", handleRootChange);
    ledgerRoot.addEventListener("submit", handleRootSubmit);
    ledgerRoot.addEventListener("keydown", handleRootKeydown);
    document.addEventListener("pointerdown", handleDocumentPointerDown);
    initialized = true;
    renderApp();
    ledgerRoot.removeAttribute("aria-busy");
    return deepClone(ledgerData);
  }

  const publicApi = {
    init,
    async refresh(force = false) {
      if (!initialized || !ledgerAdapter) return true;
      if (ledgerAdapter.busy || ledgerAdapter.pending) return false;
      if (!force && (openDialogName || editingBillId || editingNoteBillId)) return false;
      if (force && (openDialogName || editingBillId || editingNoteBillId)) {
        ledgerData = normalizeData(await ledgerAdapter.load());
        renderDirty = true;
        setNotice("已读取同行者的最新数据，保留了你的表单；请检查后重新保存。");
        return true;
      }
      captureBillDraft();
      const next = normalizeData(await ledgerAdapter.load());
      if (renderDirty || JSON.stringify(next) !== JSON.stringify(ledgerData)) { ledgerData = next; renderApp(); renderDirty = false; }
      return true;
    },
    async recoverSavedMutation(recovered) {
      const confirmed = recovered.find(entry => entry.adapter === ledgerAdapter && entry.snapshot);
      if (!confirmed || !recoveredMutation) return;
      // Consume the successful POST snapshot even if a later refresh fails.
      ledgerData = normalizeData(confirmed.snapshot);
      const changed = recoveredMutation.generation !== draftGeneration;
      if (!changed && typeof recoveredMutation.afterSuccess === "function") recoveredMutation.afterSuccess();
      recoveredMutation = null;
      if (changed) {
        renderDirty = true;
        setNotice("先前的修改已保存；保留了你随后输入的内容，请检查后再保存。");
        return;
      }
      if (initialized) renderApp();
    },
    setActiveTab,
    createLocalStorageAdapter,
    createD1Adapter,
    getPersistenceMode() {
      return ledgerPersistenceMode;
    },
    getSnapshot() {
      return ledgerData ? deepClone(ledgerData) : null;
    }
  };
  if (typeof module === "object" && module.exports) module.exports = publicApi;
  if (typeof window === "undefined" || typeof document === "undefined") return;
  window.TravelLedger = publicApi;

  // The page controller initializes Ledger only when the module is enabled.
  // Standalone consumers can continue to call TravelLedger.init(options) explicitly.
})();
