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
test('Google and Apple search by readable place and address while Apple retains WGS84 ll',t=>{
 const maps=setup(t);
 const place={countryCode:'JP',localName:'大通公園',name:'Odori Park',address:'北海道札幌市中央区大通西1-12丁目',cityOrArea:'札幌',geo:{lat:43.0599,lng:141.3475,coordinateSystem:'WGS84',source:'Verified map'},navigation:{services:{google:{url:'https://www.google.com/maps/search/?api=1&query=43.0599%2C141.3475'}}}};
 const google=maps.resolve(place);
 assert.equal(google.kind,'search');
 assert.equal(new URL(google.url).searchParams.get('query'),'大通公園, 北海道札幌市中央区大通西1-12丁目, 札幌');
 maps.choose('JP','apple');
 const apple=new URL(maps.resolve(place).url);
 assert.equal(apple.searchParams.get('q'),'大通公園, 北海道札幌市中央区大通西1-12丁目');
 assert.equal(apple.searchParams.get('ll'),'43.0599,141.3475');
});
test('coordinates are a search fallback when no readable name or address exists',t=>{
 const maps=setup(t);
 const place={countryCode:'JP',geo:{lat:43.0599,lng:141.3475,coordinateSystem:'WGS84',source:'Verified map'}};
 assert.equal(new URL(maps.resolve(place).url).searchParams.get('query'),'43.0599,141.3475');
 maps.choose('JP','apple');
 const apple=new URL(maps.resolve(place).url);
 assert.equal(apple.searchParams.get('q'),'43.0599,141.3475');
 assert.equal(apple.searchParams.get('ll'),'43.0599,141.3475');
 assert.equal(new URL(maps.resolve({...place,cityOrArea:'Sapporo'}).url).searchParams.get('q'),'Sapporo');
 maps.choose('JP','google');
 assert.equal(new URL(maps.resolve({...place,cityOrArea:'Sapporo'}).url).searchParams.get('query'),'43.0599,141.3475');
});
