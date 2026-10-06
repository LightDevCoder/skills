import { applyChanges } from "./sync.js";

const text = (value, max = 1000) => {
  if (typeof value !== "string" || !value.trim() || value.length > max)
    throw new Error("文字内容无效");
  return value.trim();
};
const object = (properties, required = Object.keys(properties)) => ({
  type: "object", properties, required, additionalProperties: false,
});
const string = { type: "string" }, boolean = { type: "boolean" };
const cents = { type: "integer", minimum: 1, maximum: 1e12 };
const definitions = {
  get_trip_context: {
    description: "Read authored itinerary, bookings, known ticket IDs and current shared records. Attachments are not sent to the model.",
    parameters: object({}),
  },
  create_task: {
    description: "Prepare an explicit new travel task. It is saved only after the shared revision check succeeds.",
    parameters: object({ text: { type: "string", maxLength: 1000 } }),
  },
  update_task: {
    description: "Prepare a completion check or text update of an existing task ID. Preserve text if omitted.",
    parameters: object({ id: string, completed: boolean, text: string }, ["id", "completed"]),
  },
  set_ticket_status: {
    description: "Prepare the local purchased/check status of an existing ticket. This does not buy, cancel or change a merchant order.",
    parameters: object({ id: string, completed: boolean }),
  },
  add_traveler: {
    description: "Prepare a named traveler for the shared ledger when explicitly requested.",
    parameters: object({ name: { type: "string", maxLength: 30 } }),
  },
  add_expense: {
    description: "Prepare a shared expense with integer cents and existing traveler IDs. Ask for missing payer, participants or converted base amount; never invent an exchange rate.",
    parameters: object({
      currency: string, originalAmountCents: cents, baseAmountCents: cents,
      payerId: string, participantIds: { type: "array", items: string, minItems: 1 },
      category: { type: "string", enum: ["餐饮", "交通", "住宿", "门票", "购物", "其他"] },
      note: { type: "string", maxLength: 160 },
    }, ["currency", "originalAmountCents", "payerId", "participantIds"]),
  },
};

export function createAiTools(data, initial) {
  const modules = data.config?.modules || {};
  const names = ["get_trip_context", ...(modules.todo ? ["create_task", "update_task"] : []),
    ...(modules.itinerary ? ["set_ticket_status"] : []),
    ...(modules.ledger ? ["add_traveler", "add_expense"] : [])];
  const tools = names.map((name) => ({ type: "function", function: { name, ...definitions[name] } }));
  const changes = new Map(), actions = new Map();
  let candidate = structuredClone(initial);
  const change = (collection, value, summary) => {
    const entry = { collection, id: value.id, op: "upsert", value };
    const key = `${collection}:${value.id}`;
    const next = applyChanges(candidate, [entry]);
    changes.set(key, entry); actions.set(key, summary); candidate = next;
    return { status: "prepared", record: value };
  };
  return {
    tools,
    async execute(name, args) {
      if (!names.includes(name)) throw new Error("不支持该操作；行程、预订和原始附件仅供查看");
      const definition = definitions[name].parameters;
      if (!args || typeof args !== "object" || Array.isArray(args) ||
          Object.keys(args).some((key) => !Object.hasOwn(definition.properties, key)) ||
          definition.required.some((key) => !Object.hasOwn(args, key)))
        throw new Error("工具参数无效");
      if (name === "get_trip_context") return {
        trip: data.trip, days: data.days, places: data.places,
        flights: data.flights, flightJourneys: data.flightJourneys,
        accommodations: data.accommodations,
        tickets: (data.ticketPlanning?.items || []).map(({ id, name, day, requirement }) => ({ id, name, day, requirement })),
        shared: candidate, capabilities: names,
        limits: "Authored itinerary/bookings/materials are read-only. No merchant orders, payments, attachment uploads or image recognition.",
      };
      if (name === "create_task") return change("todos", {
        id: `todo-ai-${crypto.randomUUID()}`, text: text(args.text), completed: false,
      }, `添加 to-do：${text(args.text)}`);
      if (name === "update_task") {
        const prior = candidate.todos.find((item) => item.id === args.id);
        if (!prior || typeof args.completed !== "boolean") throw new Error("to-do ID 或完成状态无效");
        return change("todos", { ...prior, completed: args.completed, ...(args.text !== undefined ? { text: text(args.text) } : {}) },
          `更新 to-do：${args.text === undefined ? prior.text : text(args.text)}`);
      }
      if (name === "set_ticket_status") {
        if (!(data.ticketPlanning?.items || []).some((item) => item.id === args.id) || typeof args.completed !== "boolean")
          throw new Error("票据 ID 或状态无效");
        return change("tickets", { id: args.id, completed: args.completed }, `更新票据状态：${args.id}`);
      }
      if (name === "add_traveler") return change("travelers", {
        id: `person-ai-${crypto.randomUUID()}`, name: text(args.name, 30), color: "#217D91",
      }, `添加成员：${text(args.name, 30)}`);
      const base = candidate.settings?.baseCurrency || "CNY";
      if (!Number.isSafeInteger(args.originalAmountCents) || args.originalAmountCents <= 0)
        throw new Error("金额须为正整数分");
      const amount = args.currency === base ? args.originalAmountCents : args.baseAmountCents;
      if (!Number.isSafeInteger(amount) || amount <= 0 ||
          (args.currency === base && args.baseAmountCents !== undefined && args.baseAmountCents !== amount))
        throw new Error("请提供真实的本位币换算金额；同币种金额必须一致");
      if (args.category !== undefined && !definitions.add_expense.parameters.properties.category.enum.includes(args.category))
        throw new Error("账单分类无效");
      const now = new Date().toISOString();
      return change("bills", {
        id: `bill-ai-${crypto.randomUUID()}`, currency: args.currency,
        originalAmountCents: args.originalAmountCents, baseAmountCents: amount,
        payerId: args.payerId, participantIds: args.participantIds,
        category: args.category || "其他", note: args.note === undefined || args.note === "" ? "" : text(args.note, 160),
        createdAt: now, updatedAt: now,
      }, `记录花费：${args.currency} ${(args.originalAmountCents / 100).toFixed(2)}`);
    },
    plan(message) {
      const entries = [...changes.values()];
      // Validate the complete plan too, including references created in this turn.
      if (entries.length) applyChanges(initial, entries);
      return { message, changes: entries, actions: [...actions.values()] };
    },
  };
}
