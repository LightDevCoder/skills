import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {Window} from 'happy-dom';
const read=name=>readFileSync(new URL('../'+name,import.meta.url),'utf8');
test('flight, stay and itinerary PDF tickets share an image preview, zoom and source link',t=>{
 const w=new Window({url:'http://localhost/'});t.after(()=>w.happyDOM.abort());
 w.document.body.innerHTML='<section id="flights"><button data-ticket-open="proof">Flight</button></section><section id="stays"><button data-ticket-open="proof">Stay</button></section><section id="itinerary"><button data-ticket-open="proof">Itinerary</button></section><dialog id="ticket-dialog"><h2 id="ticket-dialog-title"></h2><button id="ticket-dialog-close">Close</button><div id="ticket-dialog-body"></div></dialog>';
 w.eval(read('app.js').replace('document.addEventListener("DOMContentLoaded", init);','')+`\nstate.data={ticketPlanning:{items:[{id:'proof',name:'Proof',document:{url:'assets/tickets/proof.pdf'}}]}};setupTicketDialog();`);
 for(const selector of ['#flights button','#stays button','#itinerary button']){
  const button=w.document.querySelector(selector);button.focus();button.click();
  assert.equal(w.document.querySelector('dialog').open,true);
  const body=w.document.querySelector('#ticket-dialog-body');
  assert.equal(new URL(body.querySelector('img.ticket-dialog__preview').src).pathname,'/assets/tickets/proof.png');
  assert.equal(body.querySelectorAll('iframe').length,0);
  const source=body.querySelector('a[href$="proof.pdf"]');
  assert.ok(source);
  assert.match(source.textContent,/在新窗口打开 PDF 原件/);
  const zoom=body.querySelector('[data-ticket-zoom]');
  zoom.click();
  assert.equal(zoom.getAttribute('aria-pressed'),'true');
  assert.equal(body.querySelector('img').classList.contains('is-zoomed'),true);
  zoom.click();
  assert.equal(body.querySelector('img').classList.contains('is-zoomed'),false);
  w.document.querySelector('#ticket-dialog-close').click();
  assert.equal(w.document.activeElement,button);
 }
});
test('rental locations use canonical references or address-search fallbacks',t=>{
 const w=new Window({url:'http://localhost/'});t.after(()=>w.happyDOM.abort());
 w.eval(read('map-navigation.js'));
 w.eval(read('app.js').replace('document.addEventListener("DOMContentLoaded", init);','')+`\nwindow.testRentalNavigation=rentalNavigation;`);
 assert.match(w.testRentalNavigation({placeId:'airport',location:'Airport'},'pickup'),/data-navigation-place="airport"/);
 w.document.body.innerHTML=w.testRentalNavigation({location:'Return office',address:'Public road'},'dropoff');
 w.document.querySelector('button').click();
 assert.equal(w.document.querySelector('dialog').open,true);
 assert.match(w.document.querySelector('dialog').textContent,/Public road/);
});
