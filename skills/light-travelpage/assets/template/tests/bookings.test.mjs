import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {validateTrip} from '../scripts/validate.mjs';
const root=new URL('..',import.meta.url).pathname;
function fixture(){
 const d=JSON.parse(readFileSync(new URL('../trip-data.json',import.meta.url)));
 d.metadata={tripId:'bookings-test',title:'Test'};
 d.trip={status:'draft',startDate:'2026-10-01',endDate:'2026-10-01',dayCount:1};
 d.config.modules={flights:false,overview:false,itinerary:true,todo:false,driving:false,ledger:false};
 d.days=[{day:1,date:'2026-10-01',locations:[],schedule:[{id:'first',time:'10:00',text:'Test'}]}];
 d.accommodations=[];d.flights=[];d.flightJourneys=[];d.ticketPlanning.items=[];d.demoNavigationPlaceIds=[];return d;
}
test('accommodation dates and itinerary references are checked while legacy trips remain valid',()=>{
 const d=fixture(); assert.equal(validateTrip(d,root).ok,true);
 for(const day of d.days) for(const item of day.schedule) delete item.accommodationId;
 d.accommodations=[{id:'test-stay',name:'Test',status:'pending',checkIn:'2026-10-02',checkOut:'2026-10-01'}];
 assert.equal(validateTrip(d,root).ok,false);
 d.accommodations[0].checkOut=null; assert.equal(validateTrip(d,root).ok,true);
 d.days[0].schedule[0].accommodationId='missing'; assert.equal(validateTrip(d,root).ok,false);
});
