const $ = (selector) => document.querySelector(selector);
const codeIcons = (code) => code === 0 ? '☀️' : code < 4 ? '⛅' : code < 50 ? '🌫️' : code < 70 ? '🌧️' : code < 80 ? '🌨️' : '⛈️';
const api = async (url, options={}) => { const response = await fetch(url, {...options, headers:{'Content-Type':'application/json',...(options.headers||{})}}); const data = await response.json(); if (!response.ok) throw new Error(data.error || 'Falha na solicitação'); return data; };
const toast = (message) => { const node=$('#toast'); node.textContent=message; node.classList.add('show'); setTimeout(()=>node.classList.remove('show'),3000); };
const formatDate = (value) => value ? new Intl.DateTimeFormat('pt-BR',{day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit'}).format(new Date(value)) : '—';
const formatBytes = (value=0) => value ? new Intl.NumberFormat('pt-BR',{style:'unit',unit:'megabyte',maximumFractionDigits:1}).format(value/1048576) : '—';
const formatCapacity = (value=0) => value ? `${new Intl.NumberFormat('pt-BR',{maximumFractionDigits:1}).format(value/1073741824)} GB` : '—';
const escapeHtml = (value='') => String(value).replace(/[&<>"']/g, character=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[character]));
let calendarDate = new Date(new Date().getFullYear(),new Date().getMonth(),1);
let googleConnected = false;

function tick(){ const now=new Date(); $('#clock').textContent=now.toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit',second:'2-digit'}); $('#date').textContent=now.toLocaleDateString('pt-BR',{weekday:'long',day:'numeric',month:'long'}); }

const calendarMonthKey=()=>`${calendarDate.getFullYear()}-${String(calendarDate.getMonth()+1).padStart(2,'0')}`;
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
  const eventList=$('#month-events'); eventList.classList.toggle('empty',!events.length);
  eventList.innerHTML=events.length?events.map(event=>`<div class="month-event"><time>${formatCalendarEvent(event)}</time><strong>${escapeHtml(event.summary)}</strong></div>`).join(''):'Nenhum evento neste mês.';
}

async function loadWeather(city){
  try { const data=await api('/api/weather?city='+encodeURIComponent(city)); const current=data.current; $('#temperature').textContent=Math.round(current.temperature_2m)+'°'; $('#city-name').textContent=[data.place.name,data.place.admin1].filter(Boolean).join(', '); $('#weather-icon').textContent=codeIcons(current.weather_code); const days=data.daily; $('#forecast').innerHTML=days.time.map((date,i)=>`<div><small>${new Date(date+'T12:00').toLocaleDateString('pt-BR',{weekday:'short'})}</small><strong>${codeIcons(days.weather_code[i])} ${Math.round(days.temperature_2m_max[i])}°</strong><span>${Math.round(days.temperature_2m_min[i])}° · ${days.precipitation_probability_max[i]}%</span></div>`).join(''); }
  catch(error){ toast(error.message); }
}

function renderBackup(backup){ const state=$('#backup-state'); if(!backup){state.textContent='Sem dados';return;} const good=backup.status==='success'; state.textContent=good?'Concluído':'Falhou'; state.className='status '+(good?'good':'bad'); const values=[backup.source,formatDate(backup.finished_at),formatBytes(backup.size_bytes),`${Math.round(backup.duration_seconds||0)} s`]; document.querySelectorAll('#backup-details dd').forEach((node,i)=>node.textContent=values[i]); }

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

async function loadGoogle(){ setGoogleLoading(); try { const data=await api('/api/google/data?month='+calendarMonthKey()); googleConnected=true; $('#google-connect').textContent='Google conectado'; renderCalendar(data.events); $('#task-count').textContent=data.tasks.length; $('#tasks').classList.remove('empty'); $('#tasks').innerHTML=data.tasks.length?data.tasks.slice(0,10).map(task=>`<button class="row task" data-list="${escapeHtml(task.tasklist_id)}" data-task="${escapeHtml(task.id)}"><span>○</span><span>${escapeHtml(task.title)}</span><small>${task.due?formatDate(task.due):''}</small></button>`).join(''):'Nenhuma tarefa pendente.'; }
  catch(error){ $('#month-events').textContent='Não foi possível carregar a agenda.'; $('#tasks').textContent='Não foi possível carregar as tarefas.'; $('#task-count').textContent='—'; if(!error.message.includes('não foi conectado')) toast(error.message); }
}

async function loadDevices(selected=''){ try { const data=await api('/api/smartthings/devices'); const devices=data.items||[]; $('#device-select').innerHTML='<option value="">Selecione o aparelho</option>'+devices.map(device=>`<option value="${device.deviceId}" ${device.deviceId===selected?'selected':''}>${device.label||device.name}</option>`).join(''); } catch(error) { /* Token ainda não instalado. */ } }
async function init(){ tick(); setInterval(tick,1000); renderCalendar(); setGoogleLoading(); loadHostMetrics(); setInterval(loadHostMetrics,1000); const overview=await api('/api/overview'); const city=overview.settings.city||'Salvador'; $('#city-input').value=city; renderBackup(overview.backup); loadWeather(city); if(overview.google_connected) loadGoogle(); else setGoogleDisconnected(); if(overview.smartthings_connected) { $('#ac-state').textContent=overview.settings.smartthings_device_id?'Conectado':'Selecione o aparelho'; $('#ac-state').className='status good'; loadDevices(overview.settings.smartthings_device_id||''); } }

$('#city-button').onclick=()=>$('#settings-dialog').showModal();
$('#settings-form').onsubmit=async(event)=>{ event.preventDefault(); const city=$('#city-input').value.trim(); if(!city)return; const smartthings_device_id=$('#device-select').value; await api('/api/settings',{method:'POST',body:JSON.stringify({city,smartthings_device_id})}); $('#settings-dialog').close(); loadWeather(city); };
$('#google-connect').onclick=()=>location.href='/api/google/auth/start';
const moveCalendar=(offset)=>{calendarDate=new Date(calendarDate.getFullYear(),calendarDate.getMonth()+offset,1);renderCalendar();if(googleConnected)loadGoogle();};
$('#calendar-prev').onclick=()=>moveCalendar(-1);
$('#calendar-next').onclick=()=>moveCalendar(1);
$('#tasks').onclick=async(event)=>{const task=event.target.closest('[data-task]');if(!task)return;await api('/api/google/task/complete',{method:'POST',body:JSON.stringify({tasklist_id:task.dataset.list,task_id:task.dataset.task})});task.remove();toast('Tarefa concluída');};
document.querySelectorAll('[data-temp-step]').forEach(button=>button.onclick=()=>{$('#target-temp').textContent=Math.max(16,Math.min(30,+$('#target-temp').textContent + +button.dataset.tempStep));});
document.querySelectorAll('[data-ac]').forEach(button=>button.onclick=async()=>{try{const command=button.dataset.ac;const payload={command};if(command==='temperature')payload.value=+$('#target-temp').textContent;await api('/api/smartthings/command',{method:'POST',body:JSON.stringify(payload)});toast('Comando enviado ao ar-condicionado');}catch(error){toast(error.message);}});
$('#history-button').onclick=async()=>{const data=await api('/api/backups');$('#backup-history').innerHTML=data.items.map(item=>`<div class="row"><span class="dot"></span><span>${item.source} · ${item.status}</span><time>${formatDate(item.finished_at)}</time></div>`).join('')||'Sem histórico.';$('#history-dialog').showModal();};
$('#history-close').onclick=()=>$('#history-dialog').close();
init().catch(error=>toast(error.message));
