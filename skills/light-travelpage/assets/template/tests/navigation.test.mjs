import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {Window} from 'happy-dom';
function setup(t) { const w=new Window(); t.after(()=>w.happyDOM.abort()); w.eval(readFileSync(new URL('../map-navigation.js',import.meta.url),'utf8')); return w.TravelMaps; }
test('navigation follows destination region and per-region choice, preserving unknown coordinates as search', t=>{
 const maps=setup(t);
 assert.equal(maps.resolve({countryCode:'CN',name:'西湖'}).provider,'amap');
 assert.equal(maps.resolve({countryCode:'KR',name:'서울역'}).provider,'kakao');
 assert.equal(maps.resolve({countryCode:'RU',name:'Москва'}).provider,'yandex');
 assert.equal(maps.resolve({countryCode:'FR',name:'Paris'}).provider,'google');
 assert.equal(maps.resolve({name:'Unknown'}).provider,null);
 maps.choose('KR','apple');
 assert.equal(maps.resolve({countryCode:'KR',name:'서울역'}).provider,'apple');
 assert.equal(maps.resolve({countryCode:'CN',name:'西湖'}).provider,'amap');
 maps.choose('KR','auto');
 assert.equal(maps.resolve({countryCode:'KR',name:'서울역',geo:{lat:37,lng:127}}).kind,'search');
});
test('map URLs encode labels, respect coordinate systems, and reject unsafe destinations',t=>{
 const maps=setup(t);
 const geo={lat:37.3952969470752,lng:127.110449292622,coordinateSystem:'WGS84',source:'Kakao official guide'};
 assert.equal(maps.resolve({countryCode:'KR',name:'Kakao',geo}).url,'https://map.kakao.com/link/map/37.3952969470752,127.110449292622');
 const china={countryCode:'CN',name:'A&B # place',geo};
 assert.equal(maps.resolve(china).kind,'search');
 assert.equal(new URL(maps.resolve(china).url).searchParams.get('keyword'),'A&B # place');
 assert.equal(maps.safeUrl('javascript:alert(1)','google'),'');
 assert.equal(maps.safeUrl('https://www.google.com.evil.test/maps/search/?query=x','google'),'');
 assert.equal(maps.safeUrl('https://www.google.com/maps/search/?api=1&query=museum&code=secret','google').includes('secret'),false);
 maps.choose('KR','apple'); assert.equal(new URL(maps.resolve({countryCode:'KR',name:'Kakao',geo}).url).searchParams.get('ll'),'37.3952969470752,127.110449292622');
});
