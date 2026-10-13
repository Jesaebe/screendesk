const $ = (selector) => document.querySelector(selector);
const codeIcons = (code) => code === 0 ? '☀️' : code < 4 ? '⛅' : code < 50 ? '🌫️' : code < 70 ? '🌧️' : code < 80 ? '🌨️' : '⛈️';
const api = async (url, options={}) => { const response = await fetch(url, {...options, headers:{'Content-Type':'application/json',...(options.headers||{})}}); const data = await response.json(); if (!response.ok) throw new Error(data.error || 'Falha na solicitação'); return data; };
const toast = (message) => { const node=$('#toast'); node.textContent=message; node.classList.add('show'); setTimeout(()=>node.classList.remove('show'),3000); };
const formatDate = (value) => value ? new Intl.DateTimeFormat('pt-BR',{day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit'}).format(new Date(value)) : '—';
const formatBytes = (value=0) => value ? new Intl.NumberFormat('pt-BR',{style:'unit',unit:'megabyte',maximumFractionDigits:1}).format(value/1048576) : '—';
const formatCapacity = (value=0) => value ? `${new Intl.NumberFormat('pt-BR',{maximumFractionDigits:1}).format(value/1073741824)} GB` : '—';
const formatDuration = (value=0) => { const seconds=Math.max(0,Math.round(value||0)); return seconds<60?`${seconds} s`:`${Math.floor(seconds/60)} min ${seconds%60} s`; };
const escapeHtml = (value='') => String(value).replace(/[&<>"']/g, character=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[character]));
let calendarDate = new Date(new Date().getFullYear(),new Date().getMonth(),1);
let googleConnected = false;
let googleLoading = false;
let latestBackupRunId = '';

function enableDragScrolling(){
  const targets=document.querySelectorAll('.month-events,#tasks,#backup-history,.sources-list');
  targets.forEach(target=>{
    target.classList.add('drag-scroll');
    let startY=0; let startScroll=0; let dragged=false;
    target.addEventListener('pointerdown',event=>{if(event.pointerType!=='mouse'||event.button!==0)return;startY=event.clientY;startScroll=target.scrollTop;dragged=false;target.setPointerCapture(event.pointerId);});
    target.addEventListener('pointermove',event=>{if(!target.hasPointerCapture(event.pointerId))return;const distance=event.clientY-startY;if(Math.abs(distance)>4){dragged=true;target.classList.add('is-dragging');event.preventDefault();target.scrollTop=startScroll-distance;}});
    const stop=event=>{if(!target.hasPointerCapture(event.pointerId))return;target.releasePointerCapture(event.pointerId);target.classList.remove('is-dragging');if(dragged){target.dataset.suppressClick='true';setTimeout(()=>delete target.dataset.suppressClick,0);}};
    target.addEventListener('pointerup',stop);target.addEventListener('pointercancel',stop);
    target.addEventListener('click',event=>{if(target.dataset.suppressClick){event.preventDefault();event.stopPropagation();}},true);
  });
}

function tick(){ const now=new Date(); $('#clock').textContent=now.toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit',second:'2-digit'}); $('#date').textContent=now.toLocaleDateString('pt-BR',{weekday:'long',day:'numeric',month:'long'}); }

const calendarMonthKey=()=>`${calendarDate.getFullYear()}-${String(calendarDate.getMonth()+1).padStart(2,'0')}`;
const localDateKey=(date)=>`${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`;
const eventDateKey=(event)=>{const raw=event.start.dateTime||event.start.date||'';return event.start.date?raw.slice(0,10):localDateKey(new Date(raw));};
const formatCalendarEvent=(event)=>{const value=event.start.dateTime||event.start.date;if(!value)return '—';if(event.start.date)return `Dia ${Number(value.slice(8,10))} · dia todo`;return new Intl.DateTimeFormat('pt-BR',{day:'2-digit',hour:'2-digit',minute:'2-digit'}).format(new Date(value));};
const loading=(label)=>`<span class="loading" role="status"><i aria-hidden="true"></i>${label}</span>`;
function setGoogleLoading(){const events=$('#month-events');events.className='month-events empty';events.innerHTML=loading('Carregando agenda…');const tasks=$('#tasks');tasks.className='list empty';tasks.innerHTML=loading('Carregando tarefas…');$('#task-count').textContent='…';}
function setGoogleDisconnected(){const events=$('#month-events');events.className='month-events empty';events.textContent='Conecte o Google para carregar os eventos.';const tasks=$('#tasks');tasks.className='list empty';tasks.textContent='Conecte o Google para carregar as tarefas.';}
function renderCalendar(events=[]){
  const year=calendarDate.getFullYear(); const month=calendarDate.getMonth(); const today=new Date();
  $('#calendar-month').textContent=calendarDate.toLocaleDateString('pt-BR',{month:'long',year:'numeric'});
  const byDay=new Map();
  events.forEach(event=>{const raw=event.start.dateTime||event.start.date||'';const match=raw.match(/^(\d{4})-(\d{2})-(\d{2})/);if(!match||+match[1]!==year||+match[2]!==month+1)return;const day=+match[3];if(!byDay.has(day))byDay.set(day,[]);byDay.get(day).push(event.summary);});
  const firstDay=new Date(year,month,1).getDay(); const days=new Date(year,month+1,0).getDate(); const cells=[];
  for(let index=0;index<42;index++){const day=index-firstDay+1;if(day<1||day>days){cells.push('<span class="calendar-day outside"></span>');continue;}const summaries=byDay.get(day)||[];const isToday=day===today.getDate()&&month===today.getMonth()&&year===today.getFullYear();const label=summaries.length?`${summaries.length} evento${summaries.length>1?'s':''}: ${summaries.join(', ')}`:'';cells.push(`<span class="calendar-day${isToday?' today':''}${summaries.length?' has-event':''}" title="${escapeHtml(label)}"><b>${day}</b>${summaries.length?'<i></i>':''}</span>`);}
  $('#calendar-grid').innerHTML=cells.join('');
  const visibleEvents=events.filter(event=>eventDateKey(event)>=localDateKey(today));
  const eventList=$('#month-events'); eventList.classList.toggle('empty',!visibleEvents.length);
  eventList.innerHTML=visibleEvents.length?visibleEvents.map(event=>`<div class="month-event"><time>${formatCalendarEvent(event)}</time><strong>${escapeHtml(event.summary)}</strong></div>`).join(''):'Nenhum evento de hoje em diante neste mês.';
}

async function loadWeather(city){
  try { const data=await api('/api/weather?city='+encodeURIComponent(city)); const current=data.current; $('#temperature').textContent=Math.round(current.temperature_2m)+'°'; $('#city-name').textContent=[data.place.name,data.place.admin1].filter(Boolean).join(', '); $('#weather-icon').textContent=codeIcons(current.weather_code); const days=data.daily; $('#forecast').innerHTML=days.time.map((date,i)=>`<div><small>${new Date(date+'T12:00').toLocaleDateString('pt-BR',{weekday:'short'})}</small><strong>${codeIcons(days.weather_code[i])} ${Math.round(days.temperature_2m_max[i])}°</strong><span>${Math.round(days.temperature_2m_min[i])}° · ${days.precipitation_probability_max[i]}%</span></div>`).join(''); }
  catch(error){ toast(error.message); }
}

function renderBackup(backup,active){
  const state=$('#backup-state'); const labels=document.querySelectorAll('#backup-details dt'); const values=document.querySelectorAll('#backup-details dd');
  values[2].className=''; values[2].removeAttribute('title');
  if(active){
    state.textContent='Backup em andamento'; state.className='status running';
    ['Origem','Iniciado','Situação','Duração'].forEach((label,i)=>labels[i].textContent=label);
    const elapsed=Math.max(0,Math.floor((Date.now()-new Date(active.started_at).getTime())/1000));
    [active.display_name||active.source,formatDate(active.started_at),'Criando e enviando backup',`${Math.floor(elapsed/60)} min ${elapsed%60} s`].forEach((value,i)=>values[i].textContent=value);
    return;
  }
  if(!backup){['Origem','Concluído','Tamanho','Duração'].forEach((label,i)=>labels[i].textContent=label);state.textContent='Sem dados';state.className='status neutral';values.forEach(node=>node.textContent='—');return;}
  const good=backup.status==='success'; state.textContent=good?'Concluído':'Falhou'; state.className='status '+(good?'good':'bad');
  const detail=good?formatBytes(backup.size_bytes):(backup.error||'Falha sem detalhe disponível');
  ['Origem',good?'Concluído':'Falhou em',good?'Tamanho':'Motivo','Duração'].forEach((label,i)=>labels[i].textContent=label);
  [backup.source,formatDate(backup.finished_at),detail,`${Math.round(backup.duration_seconds||0)} s`].forEach((value,i)=>values[i].textContent=value);
  if(!good){values[2].className='backup-error';values[2].title=detail;}
}
function renderRecentBackups(items=[]){
  const list=$('#recent-backups'); const recent=items.slice(0,5);
  list.innerHTML=recent.length?recent.map(item=>{const good=item.status==='success';const label=good?'Concluído':'Falhou';const detail=good?`${formatBytes(item.size_bytes)} · ${formatDuration(item.duration_seconds)}`:(item.error||'Falha sem detalhe');return `<div class="recent-backup" title="${escapeHtml(`${label} · ${detail}`)}" aria-label="${escapeHtml(`${item.source}, ${label}, ${formatBytes(item.size_bytes)}, ${formatDuration(item.duration_seconds)}, ${formatDate(item.finished_at)}`)}"><i class="${good?'good':'bad'}" aria-hidden="true"></i><strong>${escapeHtml(item.source)}</strong><span>${formatBytes(item.size_bytes)} · ${formatDuration(item.duration_seconds)}</span><time>${formatDate(item.finished_at)}</time></div>`;}).join(''):'<span class="empty">Nenhum backup registrado.</span>';
}
function renderBackupHistory(items=[]){
  const history=$('#backup-history');
  history.innerHTML=items.length?items.map(item=>{const good=item.status==='success';const label=good?'Concluído':'Falhou';const reason=good?'':(item.error||'Falha sem detalhe');return `<div class="row history-row" title="${escapeHtml(reason)}"><span class="dot ${good?'good':'bad'}" aria-hidden="true"></span><span><strong>${escapeHtml(item.source)}</strong><small>${label} · ${formatBytes(item.size_bytes)} · ${formatDuration(item.duration_seconds)}</small></span><time>${formatDate(item.finished_at)}</time></div>`;}).join(''):'Sem histórico.';
}
async function loadRecentBackups(){try{const data=await api('/api/backups');renderRecentBackups(data.items||[]);}catch(error){/* Mantém o histórico já visível. */}}
async function loadBackupStatus(){try{const data=await api('/api/backup/status');renderBackup(data.latest,data.active);const runId=(data.latest||{}).run_id||'';if(runId&&runId!==latestBackupRunId){latestBackupRunId=runId;loadRecentBackups();}}catch(error){/* Mantém o último estado visível durante falhas transitórias. */}}

const percent=(value)=>value==null?'—':`${Math.round(value)}%`;
const setMetric=(name,value)=>{ $(`#metric-${name}`).textContent=percent(value); const meter=$(`#meter-${name}`); meter.style.width=`${Math.max(0,Math.min(100,value||0))}%`; meter.className=value>=85?'bad':value>=70?'warn':''; };
function renderHostMetrics(data){
  const current=data.current; if(!current)return;
  setMetric('cpu',current.cpu_percent); setMetric('memory',current.memory.used_percent); setMetric('root',current.root_disk.used_percent); setMetric('backup',current.backup_disk.used_percent);
  $('#metric-cpu-total').textContent=`${current.load.cpu_count} CPUs lógicas`;
  $('#metric-memory-total').textContent=`Total ${formatCapacity(current.memory.total_bytes)}`;
  $('#metric-root-total').textContent=`Total ${formatCapacity(current.root_disk.total_bytes)}`;
  $('#metric-backup-total').textContent=`Total ${formatCapacity(current.backup_disk.total_bytes)}`;
  $('#metric-swap').textContent=`Swap ${percent(current.memory.swap_used_percent)}`;
  $('#metric-load').textContent=[current.load.one,current.load.five,current.load.fifteen].map(value=>value.toFixed(2)).join(' / ');
  $('#metric-uptime').textContent=`Ativo há ${Math.floor(current.uptime_seconds/86400)} dias · ${current.load.cpu_count} CPUs`;
  ['dashboard','backup'].forEach(name=>$('#service-'+name).className='service-dot '+(current.services[name]?'good':'bad'));
  const healthy=current.services.dashboard&&current.services.backup&&current.memory.used_percent<90&&current.root_disk.used_percent<90&&current.backup_disk.used_percent<90;
  $('#host-state').textContent=healthy?'Saudável':'Atenção'; $('#host-state').className='status '+(healthy?'good':'bad');
  const samples=data.history.slice(-30); const bars=samples.map(item=>`<i title="${formatDate(item.recorded_at)} · CPU ${percent(item.cpu_percent)} · Memória ${percent(item.memory.used_percent)}"><b class="cpu" style="height:${item.cpu_percent||0}%"></b><b class="memory" style="height:${item.memory.used_percent}%"></b></i>`).join('');
  $('#metrics-history').innerHTML=bars||'<small>O histórico aparecerá após as primeiras coletas.</small>';
}
async function loadHostMetrics(){ try { renderHostMetrics(await api('/api/host/metrics')); } catch(error) { $('#host-state').textContent='Indisponível'; $('#host-state').className='status bad'; } }

async function loadGoogle(showLoading=false){
  if(googleLoading)return;
  googleLoading=true;
  if(showLoading)setGoogleLoading();
  try { const data=await api('/api/google/data?month='+calendarMonthKey()); googleConnected=true; $('#google-connect').textContent='Google conectado'; renderCalendar(data.events); $('#task-count').textContent=data.tasks.length; $('#tasks').classList.toggle('empty',!data.tasks.length); $('#tasks').innerHTML=data.tasks.length?data.tasks.map(task=>`<button class="row task" data-list="${escapeHtml(task.tasklist_id)}" data-task="${escapeHtml(task.id)}"><span>○</span><span>${escapeHtml(task.title)}</span><small>${task.due?formatDate(task.due):''}</small></button>`).join(''):'Nenhuma tarefa pendente.'; }
  catch(error){ if(showLoading){$('#month-events').textContent='Não foi possível carregar a agenda.';$('#tasks').textContent='Não foi possível carregar as tarefas.';$('#task-count').textContent='—';}if(!error.message.includes('não foi conectado'))toast(error.message); }
  finally { googleLoading=false; }
}

async function loadDevices(selected=''){ try { const data=await api('/api/smartthings/devices'); const devices=data.items||[]; $('#device-select').innerHTML='<option value="">Selecione o aparelho</option>'+devices.map(device=>`<option value="${device.deviceId}" ${device.deviceId===selected?'selected':''}>${device.label||device.name}</option>`).join(''); } catch(error) { /* Token ainda não instalado. */ } }
let backupSources=[];
const sourceForm=$('#source-form');
function sslOptions(engine,value){const values=engine==='postgresql'?[['require','Obrigatório'],['prefer','Preferencial'],['disable','Desativado'],['verify-full','Verificação completa']]:[['required','Obrigatório'],['preferred','Preferencial'],['disabled','Desativado'],['verify-identity','Verificação completa']];sourceForm.elements.sslmode.innerHTML=values.map(([id,label])=>`<option value="${id}" ${id===value?'selected':''}>${label}</option>`).join('');}
function editSource(source){sourceForm.reset();setTimeout(()=>{sourceForm.elements.id.value=source.id;sourceForm.elements.id.disabled=true;['display_name','engine','version','host','port','database','estimated_size_mb'].forEach(name=>sourceForm.elements[name].value=source[name]);sourceForm.elements.schedule.value=source.schedule.join(', ');sourceForm.elements.enabled.checked=source.enabled;sslOptions(source.engine,source.sslmode);$('#source-delete').hidden=false;},0);}
function renderSources(){const list=$('#sources-list');list.innerHTML=backupSources.map(source=>`<button type="button" data-source="${escapeHtml(source.id)}"><span><strong>${escapeHtml(source.display_name)}</strong><small>${escapeHtml(source.engine)} · ${escapeHtml(source.host)}:${source.port}/${escapeHtml(source.database)}</small></span><b class="status ${source.enabled?'good':'neutral'}">${source.enabled?'Ativo':'Pausado'}</b></button>`).join('');}
async function loadSources(){const data=await api('/api/backup/sources');backupSources=data.items;renderSources();}
async function init(){ enableDragScrolling(); tick(); setInterval(tick,1000); renderCalendar(); setGoogleLoading(); loadHostMetrics(); setInterval(loadHostMetrics,1000); const overview=await api('/api/overview'); const city=overview.settings.city||'Salvador'; $('#city-input').value=city; renderBackup(overview.backup,null); latestBackupRunId=(overview.backup||{}).run_id||''; loadRecentBackups(); loadBackupStatus(); setInterval(loadBackupStatus,1000); setInterval(loadRecentBackups,30000); loadWeather(city); if(overview.google_connected){loadGoogle(true);setInterval(()=>loadGoogle(),15000);}else setGoogleDisconnected(); if(overview.smartthings_connected) { $('#ac-state').textContent=overview.settings.smartthings_device_id?'Conectado':'Selecione o aparelho'; $('#ac-state').className='status good'; loadDevices(overview.settings.smartthings_device_id||''); } }

$('#city-button').onclick=()=>$('#settings-dialog').showModal();
$('#settings-form').onsubmit=async(event)=>{ event.preventDefault(); const city=$('#city-input').value.trim(); if(!city)return; const smartthings_device_id=$('#device-select').value; await api('/api/settings',{method:'POST',body:JSON.stringify({city,smartthings_device_id})}); $('#settings-dialog').close(); loadWeather(city); };
$('#google-connect').onclick=()=>location.href='/api/google/auth/start';
const moveCalendar=(offset)=>{calendarDate=new Date(calendarDate.getFullYear(),calendarDate.getMonth()+offset,1);renderCalendar();if(googleConnected)loadGoogle(true);};
$('#calendar-prev').onclick=()=>moveCalendar(-1);
$('#calendar-next').onclick=()=>moveCalendar(1);
$('#tasks').onclick=async(event)=>{const task=event.target.closest('[data-task]');if(!task)return;await api('/api/google/task/complete',{method:'POST',body:JSON.stringify({tasklist_id:task.dataset.list,task_id:task.dataset.task})});task.remove();$('#task-count').textContent=$('#tasks').querySelectorAll('[data-task]').length;await loadGoogle();toast('Tarefa concluída');};
document.addEventListener('visibilitychange',()=>{if(!document.hidden&&googleConnected)loadGoogle();});
document.querySelectorAll('[data-temp-step]').forEach(button=>button.onclick=()=>{$('#target-temp').textContent=Math.max(16,Math.min(30,+$('#target-temp').textContent + +button.dataset.tempStep));});
document.querySelectorAll('[data-ac]').forEach(button=>button.onclick=async()=>{try{const command=button.dataset.ac;const payload={command};if(command==='temperature')payload.value=+$('#target-temp').textContent;await api('/api/smartthings/command',{method:'POST',body:JSON.stringify(payload)});toast('Comando enviado ao ar-condicionado');}catch(error){toast(error.message);}});
$('#history-button').onclick=async()=>{const data=await api('/api/backups');renderBackupHistory(data.items||[]);$('#history-dialog').showModal();};
$('#history-close').onclick=()=>$('#history-dialog').close();
$('#sources-button').onclick=async()=>{try{await loadSources();$('#sources-dialog').showModal();}catch(error){toast(error.message);}};
$('#sources-close').onclick=()=>$('#sources-dialog').close();
$('#sources-list').onclick=(event)=>{const button=event.target.closest('[data-source]');if(button)editSource(backupSources.find(source=>source.id===button.dataset.source));};
sourceForm.elements.engine.onchange=()=>{const engine=sourceForm.elements.engine.value;sourceForm.elements.port.value=engine==='postgresql'?5432:3306;sslOptions(engine,engine==='postgresql'?'require':'required');};
const sourcePayload=()=>{const payload=Object.fromEntries(new FormData(sourceForm));payload.id=sourceForm.elements.id.value;payload.port=Number(payload.port);payload.estimated_size_mb=Number(payload.estimated_size_mb);payload.enabled=sourceForm.elements.enabled.checked;payload.timezone='America/Bahia';return payload;};
sourceForm.oninput=()=>{$('#connection-test-result').textContent='';$('#connection-test-result').className='connection-test-result';};
sourceForm.onreset=()=>setTimeout(()=>{sourceForm.elements.id.disabled=false;$('#source-delete').hidden=true;$('#connection-test-result').textContent='';sslOptions('postgresql','require');},0);
$('#source-test').onclick=async()=>{if(!sourceForm.reportValidity())return;const result=$('#connection-test-result');result.className='connection-test-result loading-result';result.innerHTML=loading('Testando conexão…');try{const response=await api('/api/backup/sources/test',{method:'POST',body:JSON.stringify(sourcePayload())});if(response.ok){result.className='connection-test-result good';result.textContent=`Conexão aprovada · ${response.version} · ${response.latency_ms} ms`;}else{result.className='connection-test-result bad';result.textContent=response.error;}}catch(error){result.className='connection-test-result bad';result.textContent=error.message;}};
sourceForm.onsubmit=async(event)=>{event.preventDefault();try{await api('/api/backup/sources',{method:'POST',body:JSON.stringify(sourcePayload())});await loadSources();sourceForm.reset();toast('Cadastro de backup salvo');}catch(error){toast(error.message);}};
$('#source-delete').onclick=async()=>{const id=sourceForm.elements.id.value;if(!confirm(`Remover ${id} do cadastro? Os backups e históricos serão preservados.`))return;try{await api('/api/backup/sources/delete',{method:'POST',body:JSON.stringify({id})});await loadSources();sourceForm.reset();toast('Origem removida do cadastro');}catch(error){toast(error.message);}};
init().catch(error=>toast(error.message));
