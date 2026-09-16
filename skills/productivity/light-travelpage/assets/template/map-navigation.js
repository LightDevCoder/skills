/* One navigation boundary for itinerary, cards and schematic pins. */
(() => {
  const names = {amap:'高德地图',apple:'Apple Maps',google:'Google Maps',kakao:'Kakao Map',yandex:'Yandex Maps'};
  const hosts = {amap:['uri.amap.com','www.amap.com','amap.com'],apple:['maps.apple.com'],google:['www.google.com','maps.google.com','maps.app.goo.gl'],kakao:['map.kakao.com'],yandex:['yandex.com','yandex.ru']};
  const parameters = {amap:['position','name','coordinate','keyword','city','view','id','src','callnative'],apple:['q','ll','address','z','coordinate','name','place-id','map'],google:['api','query','query_place_id','q','cid','ftid'],kakao:[],yandex:['text','ll','pt','z','oid']};
  let preferences = {};
  try { const saved=JSON.parse(localStorage.getItem('travel-map-preferences')||'{}'); if(saved && typeof saved==='object' && !Array.isArray(saved)) preferences=saved; } catch {}
  const region = p => /^[A-Z]{2}$/.test(p.countryCode||'') ? p.countryCode : '';
  const choices = code => code==='CN'?['amap','apple']:code==='KR'?['kakao','google','apple']:code==='RU'?['yandex','google','apple']:code?['google','apple']:Object.keys(names);
  function choose(code, provider) {
    if(provider==='auto') delete preferences[code];
    else if(choices(code).includes(provider)) preferences[code]=provider;
    try {localStorage.setItem('travel-map-preferences',JSON.stringify(preferences));} catch {}
  }
  function safeUrl(value, provider) {
    try {
      const url=new URL(value);
      if(url.protocol!=='https:' || url.username || url.password || url.port || !hosts[provider]?.includes(url.hostname)) return '';
      const allowedPath = {amap:/^\/(marker|search|detail|place\/[A-Za-z0-9]+)$/,apple:/^\/(place)?$/,google:/^\/maps(?:\/(?:search|place)(?:\/[^?#]*)?)?\/?$/,kakao:/^\/link\/(map|search)\/[^/?#]+$/,yandex:/^\/maps\/?$/};
      if(!(provider==='google' && url.hostname==='maps.app.goo.gl' && /^\/[A-Za-z0-9]+$/.test(url.pathname)) && !allowedPath[provider].test(url.pathname)) return '';
      for(const key of [...url.searchParams.keys()]) if(!parameters[provider].includes(key)) url.searchParams.delete(key);
      url.hash='';
      return url.href;
    } catch {return '';}
  }
  function resolve(place={}) {
    const code=region(place), supported=choices(code);
    const provider = supported.includes(preferences[code]) ? preferences[code] : supported.includes(place.navigation?.provider) ? place.navigation.provider : code ? supported[0] : null;
    if(!provider) return {provider:null,kind:'unavailable',url:''};
    const source=place.navigation?.services?.[provider] || {};
    const legacy=provider==='google' ? place.googleMapsUrl || place.navigation?.url : '';
    const direct=safeUrl(source.url || legacy,provider);
    if(direct) return {provider,kind:/search|[?&](q|query|text|keyword)=/.test(direct)?'search':'place',url:direct};
    const label=place.localName || place.name || place.nameZh || '';
    const query=[label,place.address,place.cityOrArea].filter(Boolean).join(', ');
    const geo=place.geo;
    const coordinate=geo && geo.source && Number.isFinite(geo.lat)&&Math.abs(geo.lat)<=90&&Number.isFinite(geo.lng)&&Math.abs(geo.lng)<=180 && geo.coordinateSystem===(provider==='amap'?'GCJ02':'WGS84');
    const id=typeof source.placeId==='string' && /^[\w-]+$/.test(source.placeId) ? source.placeId : '';
    const params=new URLSearchParams(); let base,kind=coordinate?'place':'search';
    if(provider==='amap') {
      base='https://uri.amap.com/'+(id?'detail':coordinate?'marker':'search');
      if(id) {params.set('id',id);kind='place';}
      else if(coordinate) {params.set('position',`${geo.lng},${geo.lat}`);params.set('name',label);params.set('coordinate','gaode');}
      else {params.set('keyword',query);if(place.cityOrArea)params.set('city',place.cityOrArea);}
      params.set('src','light-travelpage');params.set('callnative','0');
    } else if(provider==='kakao') {
      const target=id || (coordinate?`${geo.lat},${geo.lng}`:encodeURIComponent(query));
      return {provider,kind:id?'place':kind,url:query||coordinate||id?`https://map.kakao.com/link/${id||coordinate?'map':'search'}/${target}`:''};
    } else if(provider==='google') {
      base='https://www.google.com/maps/search/';params.set('api','1');params.set('query',coordinate?`${geo.lat},${geo.lng}`:query);
      if(id){params.set('query_place_id',id);kind='place';}
    } else if(provider==='apple') {
      base='https://maps.apple.com/';params.set('q',label||query);
      if(coordinate)params.set('ll',`${geo.lat},${geo.lng}`);else params.set('q',query);
    } else {
      base='https://yandex.com/maps/';
      if(id){params.set('oid',id);kind='place';}
      else if(coordinate){params.set('ll',`${geo.lng},${geo.lat}`);params.set('pt',`${geo.lng},${geo.lat},pm2rdm`);params.set('z','16');}
      else params.set('text',query);
    }
    return {provider,kind,url:query||coordinate||id?`${base}?${params}`:''};
  }
  const escape = value => String(value||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const fallbackPlaces = new Map();
  function button(placeId,label,fallback) {if(fallback) fallbackPlaces.set(placeId,fallback);return `<button type="button" class="schedule-map-link" data-navigation-place="${escape(placeId)}">📍 ${escape(label)}</button>`;}
  function open(place,opener) {
    let dialog=document.getElementById('navigation-dialog');
    if(!dialog){dialog=document.createElement('dialog');dialog.id='navigation-dialog';dialog.className='navigation-dialog';document.body.append(dialog);}
    const code=region(place);
    function render(){
      const result=resolve(place);
      dialog.innerHTML=`<header><h2>${escape(place.nameZh||place.name)}</h2><button type="button" data-nav-close>关闭</button></header><p data-no-translate>${escape(place.localName||place.name)}</p><p data-no-translate>${escape(place.address||place.cityOrArea)}</p><label>更换地图<select data-nav-provider aria-label="更换地图"><option value="auto">自动选择</option>${choices(code).map(p=>`<option value="${p}" ${preferences[code]===p?'selected':''}>${escape(names[p])}</option>`).join('')}</select></label><button type="button" data-nav-auto>恢复自动</button><p>${result.provider?'地图服务：'+names[result.provider]:'地区未知，请选择地图'}</p>${result.url?`<a class="navigation-open" href="${escape(result.url)}" target="_blank" rel="noopener noreferrer">用 ${escape(names[result.provider])} 打开 ↗</a>`:''}<p>${result.kind==='search'?'搜索此地点，请核对地图结果':'请核对地点后开始导航'}</p><button type="button" data-nav-copy>复制原地址</button><p data-nav-status role="status"></p><small>无法打开时，请更换地图或复制地址。地图在外部窗口打开。</small>`;
      dialog.querySelector('[data-nav-close]').onclick=()=>dialog.close();
      dialog.querySelector('[data-nav-provider]').onchange=e=>{choose(code,e.target.value);render();dialog.querySelector('[data-nav-provider]').focus();};
      dialog.querySelector('[data-nav-auto]').onclick=()=>{choose(code,'auto');render();dialog.querySelector('[data-nav-auto]').focus();};
      dialog.querySelector('[data-nav-copy]').onclick=async()=>{try{await navigator.clipboard.writeText(place.address||[place.localName||place.name,place.cityOrArea].filter(Boolean).join(', '));dialog.querySelector('[data-nav-status]').textContent='已复制';}catch{dialog.querySelector('[data-nav-status]').textContent='复制失败，请选择上方地址手动复制';}};
      window.TravelI18n?.apply(dialog);
    }
    render();if(!dialog.open)dialog.showModal();dialog.onclose=()=>opener?.focus();
  }
  document.addEventListener('click',e=>{
    const trigger=e.target.closest('[data-navigation-place]');if(!trigger)return;
    const place=window.TRAVEL_PLAN_DATA?.places?.find(p=>p.id===trigger.dataset.navigationPlace) || fallbackPlaces.get(trigger.dataset.navigationPlace);
    if(place){e.preventDefault();open(place,trigger);}
  });
  window.TravelMaps={resolve,choose,choices,safeUrl,button,open};
})();
