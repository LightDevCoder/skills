import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { Window } from 'happy-dom';
import { CURRENCY_CATALOG } from '../currencies.js';

const source = (await readFile(new URL('../ledger.js', import.meta.url), 'utf8'))
  .replace(/^import .*?;\s*/, 'const CURRENCY_CATALOG = window.testCurrencies;\n');
const initial = () => ({version:1, settings:{baseCurrency:'CNY',commonCurrencies:[],lastCurrency:'CNY'},
  travelers:[{id:'alice',name:'Alice',color:'#123456'}], bills:[]});
async function setup(t) {
  const window = new Window({url:'http://localhost/'});
  t.after(() => window.happyDOM.abort());
  window.testCurrencies = CURRENCY_CATALOG;
  window.document.body.innerHTML = '<div id="ledger-root"></div>';
  let remote = initial(), fail = null, calls = 0;
  const adapter = {mode:'d1',pending:false, load:async()=>structuredClone(remote),
    save:async(next)=>{calls++; if(fail) {adapter.pending=!fail.status || fail.status>=500; const error=fail; fail=null; throw error;} remote=structuredClone(next);}};
  window.eval(source);
  await window.TravelLedger.init({root:'#ledger-root',tripId:'test',config:{},repository:adapter});
  const $ = selector => window.document.querySelector(selector);
  const input = (selector,value) => {const el=$(selector); el.value=value; el.dispatchEvent(new window.Event('input',{bubbles:true}));};
  const settle = () => new Promise(resolve=>setTimeout(resolve,15));
  const submit = async selector => {$(selector).dispatchEvent(new window.Event('submit',{bubbles:true,cancelable:true})); await settle();};
  return {window,$,input,submit,adapter, get remote(){return remote;},set remote(value){remote=value;},
    set fail(value){fail=value;},get calls(){return calls;}};
}

test('member conflict refresh preserves form and permits explicit retry', async t => {
  const h=await setup(t);
  h.$('[data-ledger-action="open-members"]').click();
  h.input('[data-ledger-form="member-add"] input[name="name"]','Bob');
  h.remote.travelers.push({id:'carol',name:'Carol',color:'#234567'});
  h.fail=Object.assign(new Error('Conflict: refresh and retry'),{status:409});
  await h.submit('[data-ledger-form="member-add"]');
  assert.equal(h.$('[data-ledger-form="member-add"] input[name="name"]').value,'Bob');
  assert.equal(await h.window.TravelLedger.refresh(true),true);
  assert.equal(h.$('[data-ledger-form="member-add"] input[name="name"]').value,'Bob');
  await h.submit('[data-ledger-form="member-add"]');
  assert.deepEqual(h.remote.travelers.map(p=>p.name),['Alice','Carol','Bob']);
});

test('unrelated task retry leaves new bill draft untouched', async t => {
  const h=await setup(t);
  h.input('[name="originalAmount"]','123.45');
  h.input('[data-ledger-form="bill"] [name="note"]','Unsent draft');
  await h.window.TravelLedger.recoverSavedMutation([{}]);
  await h.window.TravelLedger.refresh(true);
  assert.equal(h.$('[name="originalAmount"]').value,'123.45');
  assert.equal(h.$('[data-ledger-form="bill"] [name="note"]').value,'Unsent draft');
  assert.equal(h.calls,0);
});

test('failed bill retry preserves newer edits and clears only the submitted draft', async t => {
  const h=await setup(t);
  h.input('[name="originalAmount"]','20');
  h.$('[name="payerId"][value="alice"]').checked=true;
  h.$('[name="participantIds"]').checked=true;
  h.fail=new Error('Connection lost');
  await h.submit('[data-ledger-form="bill"]');
  assert.equal(h.calls,1);
  h.input('[name="originalAmount"]','25');
  h.adapter.pending=false;
  await h.window.TravelLedger.recoverSavedMutation([{adapter:h.adapter,snapshot:h.remote}]);
  assert.equal(h.$('[name="originalAmount"]').value,'25');
  h.fail=new Error('Connection lost');
  await h.submit('[data-ledger-form="bill"]');
  h.adapter.pending=false;
  await h.window.TravelLedger.recoverSavedMutation([{adapter:h.adapter,snapshot:h.remote}]);
  assert.equal(h.$('[name="originalAmount"]').value,'');
});

test('member retry preserves newer DOM input and refreshes saved members after closing', async t => {
  const h=await setup(t);
  h.$('[data-ledger-action="open-members"]').click();
  h.input('[data-ledger-form="member-add"] input[name="name"]','Bob');
  h.fail=new Error('lost response');
  await h.submit('[data-ledger-form="member-add"]');
  h.input('[data-ledger-form="member-add"] input[name="name"]','Bobby');
  h.remote.travelers.push({id:'bob',name:'Bob',color:'#123456'});
  h.adapter.pending=false;
  await h.window.TravelLedger.recoverSavedMutation([{adapter:h.adapter,snapshot:h.remote}]);
  await h.window.TravelLedger.refresh(true);
  assert.equal(h.$('[data-ledger-form="member-add"] input[name="name"]').value,'Bobby');
  h.$('[data-ledger-dialog="members"] [data-ledger-action="close-dialog"]').click();
  await h.window.TravelLedger.refresh();
  assert.ok(h.$('#ledger-root').textContent.includes('Bob'));
});

test('unchanged member retry renders the confirmed server snapshot immediately', async t => {
  const h=await setup(t);
  h.$('[data-ledger-action="open-members"]').click();
  h.input('[data-ledger-form="member-add"] input[name="name"]','Bob');
  h.fail=new Error('lost response');
  await h.submit('[data-ledger-form="member-add"]');
  h.remote.travelers.push({id:'bob',name:'Bob',color:'#123456'});
  h.adapter.pending=false;
  await h.window.TravelLedger.recoverSavedMutation([{adapter:h.adapter,snapshot:h.remote}]);
  assert.ok(h.$('[data-ledger-dialog="members"]').textContent.includes('Bob'));
});

test('confirmed retry is consumed even when subsequent GET fails', async t => {
  const h=await setup(t);
  h.input('[name="originalAmount"]','20');
  h.$('[name="payerId"][value="alice"]').checked=true;
  h.fail=new Error('lost response');
  await h.submit('[data-ledger-form="bill"]');
  h.remote.bills.push({id:'confirmed',currency:'CNY',originalAmountCents:2000,baseAmountCents:2000,payerId:'alice',participantIds:['alice'],category:'餐饮'});
  h.adapter.pending=false;
  h.adapter.load=async()=>{throw new Error('GET unavailable');};
  await h.window.TravelLedger.recoverSavedMutation([{adapter:h.adapter,snapshot:h.remote}]);
  await assert.rejects(h.window.TravelLedger.refresh(true),/GET unavailable/);
  assert.equal(h.$('[name="originalAmount"]').value,'');
  assert.equal(h.window.TravelLedger.getSnapshot().bills[0].id,'confirmed');
  await h.submit('[data-ledger-form="bill"]');
  assert.equal(h.calls,1);
  assert.equal(h.remote.bills.length,1);
});

test('save rejected by pending guard cannot replace the original recovery draft generation', async t => {
  const h=await setup(t);
  h.input('[name="originalAmount"]','20');
  h.$('[name="payerId"][value="alice"]').checked=true;
  h.adapter.save=async()=>{h.adapter.pending=true;throw new Error('uncertain or pending');};
  await h.submit('[data-ledger-form="bill"]');
  h.input('[name="originalAmount"]','25');
  await h.submit('[data-ledger-form="bill"]');
  h.remote.bills.push({id:'confirmed',currency:'CNY',originalAmountCents:2000,baseAmountCents:2000,payerId:'alice',participantIds:['alice'],category:'餐饮'});
  h.adapter.pending=false;
  await h.window.TravelLedger.recoverSavedMutation([{adapter:h.adapter,snapshot:h.remote}]);
  assert.equal(h.$('[name="originalAmount"]').value,'25');
  assert.equal(h.window.TravelLedger.getSnapshot().bills[0].id,'confirmed');
});
