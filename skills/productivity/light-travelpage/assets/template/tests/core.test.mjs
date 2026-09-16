import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { DatabaseSync } from "node:sqlite";
import { authenticate, digest, sessionValid } from "../server/auth.js";
import { handleTrip, emptyState, applyChanges } from "../server/sync.js";
import { validateTrip, validDate } from "../scripts/validate.mjs";
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
function fixture() {
  const d = JSON.parse(fs.readFileSync(path.join(root, "trip-data.json")));
  Object.assign(d.metadata, { tripId: "fixture", title: "Fictional test" });
  Object.assign(d.trip, {
    status: "draft",
    startDate: "2026-10-01",
    endDate: "2026-10-01",
    dayCount: 1,
  });
  d.days = [
    {
      day: 1,
      date: "2026-10-01",
      title: "Fixture",
      locations: [],
      schedule: [],
    },
  ];
  d.config.modules = {
    flights: false,
    overview: false,
    itinerary: true,
    todo: true,
    driving: false,
    ledger: true,
  };
  d.preTrip.packingItems = [];
  d.ticketPlanning.items = [];
  d.flights = [];
  d.flightJourneys = [];
  d.places = [];
  d.accommodations = [];
  d.demoNavigationPlaceIds = [];
  return d;
}
function database() {
  const db = new DatabaseSync(":memory:");
  db.exec(
    fs.readFileSync(path.join(root, "migrations/0001_state.sql"), "utf8"),
  );
  function prepare(sql) {
    return {
      bind(...args) {
        return {
          async first() {
            return db.prepare(sql).get(...args) || null;
          },
          async run() {
            const r = db.prepare(sql).run(...args);
            return { meta: { changes: Number(r.changes) } };
          },
        };
      },
    };
  }
  return {
    prepare,
    async batch(statements) {
      db.exec("BEGIN");
      try {
        const result = [];
        for (const s of statements) result.push(await s.run());
        db.exec("COMMIT");
        return result;
      } catch (error) {
        db.exec("ROLLBACK");
        throw error;
      }
    },
    close() {
      db.close();
    },
  };
}

async function setup() {
  const env = {
    TRIP_ID: "fixture",
    SESSION_SECRET: "test-session-secret-".repeat(3),
    ACCESS_CODE_HASH: await digest("fictional-access-code"),
    DB: database(),
    ASSETS: { fetch: async () => Response.json(fixture()) },
  };
  const login = await authenticate({
    env,
    request: new Request("https://example.test/auth/login", {
      method: "POST",
      headers: {
        origin: "https://example.test",
        "content-type": "application/x-www-form-urlencoded",
      },
      body: "code=fictional-access-code",
    }),
  });
  const cookie = login.headers.get("set-cookie").split(";")[0];
  const call = (method = "GET", body, trip = "fixture") =>
    handleTrip({
      env,
      params: { tripId: trip },
      request: new Request(`https://example.test/api/trip/${trip}`, {
        method,
        headers: { cookie, origin: "https://example.test" },
        ...(body ? { body: JSON.stringify(body) } : {}),
      }),
    });
  return { env, cookie, call };
}
const todo = (id, text = id) => ({
  collection: "todos",
  id,
  op: "upsert",
  value: { id, text, completed: false },
});
test("calendar and null draft handling", () => {
  assert.equal(validDate("2026-02-29"), false);
  assert.equal(validDate("2028-02-29"), true);
  const d = fixture();
  assert.equal(validateTrip(d, root).ok, true);
  d.trip.startDate = null;
  d.trip.endDate = null;
  d.days[0].date = null;
  assert.equal(validateTrip(d, root).ok, true);
});
test("bad dates, backwards span and dangling references fail", () => {
  const d = fixture();
  d.trip.startDate = "2026-99-99";
  d.days[0].date = "not-a-date";
  d.days[0].schedule = [
    {
      id: "s1",
      time: "25:99",
      type: "note",
      text: "fixture",
      ticketIds: ["missing"],
    },
  ];
  const result = validateTrip(d, root);
  assert.equal(result.ok, false);
  assert.ok(result.errors.some((x) => x.includes("Unknown ticket")));
  assert.ok(result.errors.some((x) => x.includes("time invalid")));
});
test("ticket asset traversal and invalid map coordinates fail", () => {
  const d = fixture();
  d.ticketPlanning.items = [
    {
      id: "t",
      day: 1,
      document: { url: "assets/../private.pdf", type: "application/pdf" },
    },
  ];
  d.config.modules.overview = true;
  d.map = {
    mapMode: "template-auto",
    places: [{ id: "p", geo: { lat: 200, lng: 0 } }],
    routes: [{ day: 99, placeIds: ["p", "q"] }],
    dailyRoutes: [],
  };
  assert.equal(validateTrip(d, root).ok, false);
});
test("fail closed for missing auth and private assets", async () => {
  const s = await setup();
  for (const route of ["/", "/trip-data.json", "/assets/tickets/test.pdf"])
    assert.equal(
      (
        await authenticate({
          env: s.env,
          request: new Request(`https://example.test${route}`),
        })
      ).status,
      303,
    );
  assert.equal(
    (
      await authenticate({
        env: {},
        request: new Request("https://example.test/"),
      })
    ).status,
    503,
  );
  assert.equal(
    (
      await authenticate({
        env: s.env,
        request: new Request("https://example.test/api/trip/fixture"),
      })
    ).status,
    401,
  );
  s.env.DB.close();
});
test("signed session, code rotation, bad login and cross-origin writes", async () => {
  const s = await setup();
  const r = new Request("https://example.test/", {
    headers: { cookie: s.cookie },
  });
  assert.equal(await sessionValid(r, s.env), true);
  assert.equal(
    await sessionValid(r, {
      ...s.env,
      ACCESS_CODE_HASH: await digest("rotated"),
    }),
    false,
  );
  assert.equal(
    (
      await authenticate({
        env: s.env,
        request: new Request("https://example.test/auth/login", {
          method: "POST",
          headers: { origin: "https://evil.test" },
          body: "code=fictional-access-code",
        }),
      })
    ).status,
    403,
  );
  s.env.DB.close();
});
test("server rejects other trips and unauthenticated direct handler", async () => {
  const s = await setup();
  assert.equal((await s.call("GET", null, "other")).status, 403);
  assert.equal(
    (
      await handleTrip({
        env: s.env,
        params: { tripId: "fixture" },
        request: new Request("https://example.test/api/trip/fixture"),
      })
    ).status,
    401,
  );
  s.env.DB.close();
});
test("D1 contract: persist, retry, conflict and changed duplicate ID", async () => {
  const s = await setup();
  let current = await (await s.call()).json();
  assert.equal(current.revision, 0);
  const body = {
    mutationId: "request-1",
    expectedRevision: 0,
    changes: [todo("one")],
  };
  assert.equal((await s.call("POST", body)).status, 200);
  const repeat = await (await s.call("POST", body)).json();
  assert.equal(repeat.revision, 1);
  assert.equal(repeat.todos.length, 1);
  assert.equal(
    (await s.call("POST", { ...body, changes: [todo("different")] })).status,
    409,
  );
  assert.equal(
    (await s.call("POST", { ...body, mutationId: "request-2" })).status,
    409,
  );
  s.env.DB.close();
});
test("shared settings persist and invalid bill cannot mutate state", async () => {
  const s = await setup();
  await s.call();
  const response = await s.call("POST", {
    mutationId: "settings-1",
    expectedRevision: 0,
    changes: [
      {
        collection: "settings",
        id: "settings",
        op: "upsert",
        value: {
          baseCurrency: "CNY",
          commonCurrencies: ["EUR"],
          lastCurrency: "CNY",
        },
      },
    ],
  });
  assert.equal(response.status, 200);
  assert.equal((await (await s.call()).json()).settings.baseCurrency, "CNY");
  assert.equal(
    (
      await s.call("POST", {
        mutationId: "bill-bad",
        expectedRevision: 1,
        changes: [
          {
            collection: "bills",
            id: "b1",
            op: "upsert",
            value: { id: "b1", baseAmountCents: -1 },
          },
        ],
      })
    ).status,
    400,
  );
  assert.equal((await (await s.call()).json()).revision, 1);
  s.env.DB.close();
});
test("valid integer-cent bill and member references", () => {
  const changes = [
    {
      collection: "travelers",
      id: "p1",
      op: "upsert",
      value: { id: "p1", name: "Test" },
    },
    {
      collection: "bills",
      id: "b1",
      op: "upsert",
      value: {
        id: "b1",
        baseAmountCents: 1001,
        originalAmountCents: 1001,
        currency: "CNY",
        payerId: "p1",
        participantIds: ["p1"],
      },
    },
  ];
  const next = applyChanges(emptyState(), changes);
  assert.equal(next.bills[0].baseAmountCents, 1001);
  assert.throws(
    () =>
      applyChanges(next, [{ collection: "travelers", id: "p1", op: "delete" }]),
    /不存在/,
  );
});
function client() {
  const source = fs.readFileSync(path.join(root, "runtime-storage.js"), "utf8");
  const m = { exports: {} };
  new Function("module", "exports", source)(m, m.exports);
  return m.exports;
}
test("client preserves exact uncertain request, including after reload", async () => {
  const original = globalThis.fetch;
  const values = new Map(),
    journal = {
      getItem: (k) => values.get(k) || null,
      setItem: (k, v) => values.set(k, v),
      removeItem: (k) => values.delete(k),
    };
  let firstBody;
  try {
    globalThis.fetch = async (_url, options) => {
      if (options.method === "GET") return Response.json(emptyState());
      firstBody = options.body;
      throw new Error("network lost after commit");
    };
    const a = client().createD1Adapter({
      tripId: "fixture",
      collections: ["todos"],
      journal,
    });
    await a.load();
    await assert.rejects(
      a.applyChange("todos", { id: "t1", text: "test", completed: false }),
    );
    assert.equal(a.pending, true);
    const b = client().createD1Adapter({
      tripId: "fixture",
      collections: ["todos"],
      journal,
    });
    globalThis.fetch = async (_url, options) => {
      assert.equal(options.body, firstBody);
      return Response.json({
        ...emptyState(),
        revision: 1,
        todos: [{ id: "t1", text: "test", completed: false }],
      });
    };
    await b.retry();
    assert.equal(b.pending, false);
    assert.equal(values.size, 0);
  } finally {
    globalThis.fetch = original;
  }
});
test("client requires observed revision and does not leak to cross-origin API", async () => {
  const runtime = client();
  assert.throws(() =>
    runtime.createD1Adapter({
      tripId: "fixture",
      collections: ["todos"],
      apiBase: "//evil.test",
    }),
  );
  const a = runtime.createD1Adapter({
    tripId: "fixture",
    collections: ["todos"],
  });
  await assert.rejects(a.save(emptyState()), /尚未/);
});

test('damaged backup is rejected before any network operation', async () => {
  const original = globalThis.fetch; let calls=0;
  globalThis.fetch=async()=>{calls++;throw new Error('must not request');};
  try {
    const runtime=client();
    for(const snapshot of [undefined,null,{}, {...emptyState(),bills:null}, {...emptyState(),todos:[null]}]) {
      await assert.rejects(runtime.restoreSnapshot({tripId:'fixture'}, {format:'light-travelpage-backup-v1',tripId:'fixture',snapshot},0));
    }
    assert.equal(calls,0);
  } finally {globalThis.fetch=original;}
});
test('unsupported currencies fail atomically in bills and settings', () => {
  assert.throws(()=>applyChanges(emptyState(), [{collection:'settings',id:'settings',op:'upsert',value:{baseCurrency:'ZZZ',commonCurrencies:[],lastCurrency:'ZZZ'}}]));
  assert.throws(()=>applyChanges(emptyState(), [{collection:'travelers',id:'p1',op:'upsert',value:{id:'p1',name:'Test'}},{collection:'bills',id:'b1',op:'upsert',value:{id:'b1',originalAmountCents:100,baseAmountCents:100,currency:'ZZZ',payerId:'p1',participantIds:['p1']}}]));
});
test('Pages catch-all array route is accepted for exactly one trip segment',async()=>{
  const s=await setup();const request=new Request('https://example.test/api/trip/fixture',{headers:{cookie:s.cookie}});
  assert.equal((await handleTrip({env:s.env,params:{tripId:['fixture']},request})).status,200);
  assert.equal((await handleTrip({env:s.env,params:{tripId:['fixture','nested']},request})).status,403);
  s.env.DB.close();
});

test('journal cleanup failure cannot roll back a confirmed server save', async () => {
  const savedFetch=globalThis.fetch;
  const journal={getItem:()=>null,setItem:()=>{},removeItem:()=>{throw new Error('storage unavailable');}};
  let server={...emptyState(),revision:0};
  try {
    globalThis.fetch=async (_url,options)=>{
      if(options.method==='POST') {
        const body=JSON.parse(options.body);
        assert.equal(body.expectedRevision,server.revision);
        server={...applyChanges(server,body.changes),revision:server.revision+1};
      }
      return Response.json(server);
    };
    const adapter=client().createD1Adapter({tripId:'fixture',collections:['todos'],journal});
    const snapshot=await adapter.load();
    snapshot.todos.push({id:'first',text:'First saved record',completed:false});
    await adapter.save(snapshot);
    assert.equal(snapshot.revision,1);
    assert.equal(adapter.pending,false);
    snapshot.todos.push({id:'second',text:'Second saved record',completed:false});
    await adapter.save(snapshot);
    assert.deepEqual(server.todos.map(x=>x.id),['first','second']);
  } finally {globalThis.fetch=savedFetch;}
});

test('uncertain request survives expired login and retries the identical body', async () => {
  const savedFetch=globalThis.fetch, values=new Map();
  const journal={getItem:k=>values.get(k)||null,setItem:(k,v)=>values.set(k,v),removeItem:k=>values.delete(k)};
  let exactBody, phase=0;
  try {
    globalThis.fetch=async (_url,options)=>{
      if(options.method==='GET') return Response.json({...emptyState(),revision:0});
      if(!exactBody)exactBody=options.body;
      assert.equal(options.body,exactBody);
      if(phase===0)throw new Error('lost response');
      if(phase===1)return Response.json({error:'Please log in'},{status:401});
      return Response.json({...emptyState(),revision:1,todos:[{id:'saved',text:'One record',completed:false}]});
    };
    const adapter=client().createD1Adapter({tripId:'fixture',collections:['todos'],journal});
    await adapter.load();
    await assert.rejects(adapter.applyChange('todos',{id:'saved',text:'One record',completed:false}));
    phase=1;
    await assert.rejects(adapter.retry(),{status:401});
    assert.equal(adapter.pending,true);assert.equal(values.size,1);
    phase=2;
    const reloaded=client().createD1Adapter({tripId:'fixture',collections:['todos'],journal});
    assert.equal((await reloaded.retry()).todos.length,1);
    assert.equal(values.size,0);
  } finally {globalThis.fetch=savedFetch;}
});

test('batch recovery delivers successful snapshots when another adapter still fails', async () => {
  const savedFetch=globalThis.fetch;let recovering=false;
  try {
    globalThis.fetch=async (url,options)=>{
      if(options.method==='GET')return Response.json({...emptyState(),revision:0});
      if(!recovering || url.endsWith('/second'))throw new Error('still offline');
      return Response.json({...emptyState(),revision:1,todos:[{id:'a',text:'saved',completed:false}]});
    };
    const runtime=client();
    const a=runtime.createD1Adapter({tripId:'first',collections:['todos']});
    const b=runtime.createD1Adapter({tripId:'second',collections:['todos']});
    for(const adapter of [a,b]){
      await adapter.load();
      await assert.rejects(adapter.applyChange('todos',{id:'a',text:'saved',completed:false}));
    }
    recovering=true;
    const recovered=await runtime.retryAll();
    assert.equal(recovered[0].adapter,a);assert.equal(recovered[0].snapshot.todos.length,1);
    assert.equal(recovered[1].adapter,b);assert.match(recovered[1].error.message,/offline/);
    assert.equal(a.pending,false);assert.equal(b.pending,true);
  } finally {globalThis.fetch=savedFetch;}
});

test('only the translation runtime is publicly readable for bilingual sign-in', async()=>{
 const env={TRIP_ID:'fixture',SESSION_SECRET:'x'.repeat(40),ACCESS_CODE_HASH:await digest('test')};
 assert.equal(await authenticate({env,request:new Request('https://example.test/i18n.js')}),null);
 for(const route of ['/trip-data.json','/assets/tickets/demo.pdf','/map-navigation.js']) {
  const denied=await authenticate({env,request:new Request('https://example.test'+route)});
  assert.equal(denied.status,303);
 }
});
