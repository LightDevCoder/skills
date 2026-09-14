(() => {
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const pending=v=>esc(v||'待补充');
  const authored=v=>`<span data-authored>${pending(v)}</span>`;
  function render(data){
    const enabled=data.config.modules.accommodations ?? Boolean(data.accommodations?.length);
    document.querySelectorAll('[data-module="accommodations"]').forEach(e=>e.hidden=!enabled);
    const root=document.getElementById('accommodation-cards');
    if(!root)return;
    root.innerHTML=(data.accommodations||[]).map(stay=>{
      const place=data.places.find(p=>p.id===stay.placeId);
      const nights=stay.checkIn&&stay.checkOut?(Date.parse(stay.checkOut)-Date.parse(stay.checkIn))/86400000:null;
      const tickets=(stay.ticketIds||[]).map(id=>data.ticketPlanning.items.find(t=>t.id===id)).filter(Boolean);
      return `<article class="stay-card" id="stay-${esc(stay.id)}"><p class="section-kicker">STAY</p><span class="soft-label">${stay.demo?'演示资料 · ':''}${(!stay.status||stay.status==='pending')?'资料待补充':stay.status==='confirmed'?'预订已确认':'预订状态待确认'}</span><h3>${pending(stay.name||place?.name)}</h3>${place?.localName?`<p data-no-translate>${esc(place.localName)}</p>`:''}<p ${(stay.address||place?.address) && !stay.demo ? "data-no-translate" : ""}>${pending(stay.address||place?.address)}</p><dl><div><dt>入住</dt><dd>${pending(stay.checkIn)} ${esc(stay.checkInTime||'')}</dd></div><div><dt>退房</dt><dd>${pending(stay.checkOut)} ${esc(stay.checkOutTime||'')}</dd></div><div><dt>晚数</dt><dd>${nights===null?'待补充':nights}</dd></div><div><dt>房型</dt><dd>${pending(stay.roomType)}</dd></div></dl>${stay.price?`<p>${esc(stay.price.currency)} ${esc(stay.price.amount)}</p>`:''}${stay.confirmationNumber?`<p>确认号：<span data-no-translate>${esc(stay.confirmationNumber)}</span></p>`:''}<p>取消条款：${authored(stay.cancellationPolicy)}</p>${stay.missingFields?.length?`<p>待补充信息：${stay.missingFields.map(authored).join(' · ')}</p>`:''}${stay.navigationNote?`<p>${authored(stay.navigationNote)}</p>`:''}${place?TravelMaps.button(place.id,'查看地图'):''}${tickets.map(t=>`<button type="button" class="schedule-ticket__open" data-ticket-open="${esc(t.id)}">查看票据 · ${authored(t.name)}</button>`).join('')}</article>`;
    }).join('')||'<p>住宿资料待补充</p>';
    if(data.config.demo && data.demoNavigationPlaceIds?.length){
      const section=document.createElement('section');section.className='section';section.id='map-examples';
      section.innerHTML='<h2>地区地图演示</h2><p>以下是真实公共地点，用于测试地图，不属于本次行程。</p>'+data.demoNavigationPlaceIds.map(id=>data.places.find(p=>p.id===id)).filter(Boolean).map(p=>TravelMaps.button(p.id,p.nameZh||p.name)).join('');
      document.querySelector('#main .footer').before(section);
    }
    if(data.config.demo){const p=document.createElement('p');p.className='demo-notice';p.textContent='虚构示例，不可用于出行';document.querySelector('.hero').append(p);}
  }
  document.addEventListener('travel-data-ready',e=>render(e.detail));
})();
