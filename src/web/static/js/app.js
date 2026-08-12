lucide.createIcons();

// ---------- THEME DATA ----------
const THEME_COLORS = { nova:'#0b0c14', bloom:'#fdf3f6', halftone:'#fff6e0', terra:'#f4f1e8', arcade:'#07060f', ink:'#fafafa' };
const THEMES = [
  { id:'nova', name:'Nova', sub:'Professional', icon:'◆', bg:'linear-gradient(135deg,#8b7cf6,#0b0c14)' },
  { id:'bloom', name:'Bloom', sub:'Fashion / soft', icon:'✿', bg:'linear-gradient(135deg,#e8628f,#fdf3f6)' },
  { id:'halftone', name:'Halftone', sub:'Comic / pop-art', icon:'★', bg:'linear-gradient(135deg,#ff3d5a,#ffe9a8)' },
  { id:'terra', name:'Terra', sub:'Nature / calm', icon:'❦', bg:'linear-gradient(135deg,#5c7a4f,#f4f1e8)' },
  { id:'arcade', name:'Arcade', sub:'Neon / gaming', icon:'▲', bg:'linear-gradient(135deg,#00f0ff,#07060f)' },
  { id:'ink', name:'Ink', sub:'Manga / anime', icon:'✺', bg:'linear-gradient(135deg,#e6002e,#ffffff)' },
];

function setTheme(id){
  document.documentElement.setAttribute('data-theme', id);
  document.querySelectorAll('.swatch').forEach(s=>s.classList.toggle('active', s.dataset.t===id));
  document.querySelectorAll('.theme-card').forEach(c=>c.classList.toggle('selected', c.dataset.t===id));
  const meta = document.getElementById('theme-color-meta');
  if(meta && THEME_COLORS[id]) meta.setAttribute('content', THEME_COLORS[id]);
  document.getElementById('theme-sheet')?.classList.remove('open');
}

document.querySelectorAll('.swatch').forEach(s=>{
  s.addEventListener('click', ()=> setTheme(s.dataset.t));
});

function buildThemeGallery(containerId){
  const el = document.getElementById(containerId);
  if(!el) return;
  el.innerHTML = THEMES.map(t=>`
    <div class="theme-card" data-t="${t.id}">
      <div class="theme-preview" style="background:${t.bg}; color:#fff;">${t.icon}</div>
      <div class="theme-label">${t.name}<small>${t.sub}</small></div>
    </div>`).join('');
  el.querySelectorAll('.theme-card').forEach(c=>{
    c.addEventListener('click', ()=> setTheme(c.dataset.t));
  });
}
buildThemeGallery('onboard-theme-gallery');
buildThemeGallery('settings-theme-gallery');
setTheme('nova');

// ---------- NAV ----------
const screenLabels = {
  onboarding:'Setup', dashboard:'Dashboard', chat:'Chat', skills:'Skills',
  automations:'Automations', memory:'Memory', permissions:'Permissions',
  integrations:'Integrations', settings:'Settings', profile:'Execution Profile',
  diagnostics:'Diagnostics'
};
document.querySelectorAll('.nav-item[data-screen]').forEach(btn=>{
  btn.addEventListener('click', ()=>{
    const target = btn.dataset.screen;
    document.querySelectorAll('.nav-item').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));
    document.getElementById('screen-'+target).classList.add('active');
    document.getElementById('topbar-label').textContent = screenLabels[target];
    document.querySelector('.content').scrollTop = 0;
    closeDrawer();
  });
});

// ---------- MOBILE DRAWER (hamburger nav) ----------
const sidebarEl = document.getElementById('sidebar');
const backdropEl = document.getElementById('drawer-backdrop');
function openDrawer(){ sidebarEl.classList.add('open'); backdropEl.classList.add('open'); }
function closeDrawer(){ sidebarEl.classList.remove('open'); backdropEl.classList.remove('open'); }
document.getElementById('hamburger-btn').addEventListener('click', openDrawer);
document.getElementById('drawer-close').addEventListener('click', closeDrawer);
backdropEl.addEventListener('click', closeDrawer);

// ---------- MOBILE THEME SHEET ----------
const themeToggleBtn = document.getElementById('theme-toggle-btn');
const themeSheet = document.getElementById('theme-sheet');
themeToggleBtn.addEventListener('click', (e)=>{ e.stopPropagation(); themeSheet.classList.toggle('open'); });
document.addEventListener('click', (e)=>{
  if(!themeSheet.contains(e.target) && e.target!==themeToggleBtn) themeSheet.classList.remove('open');
});

// ---------- APP STATE (in-memory, drives personalization) ----------
const appState = {
  focusAreas: new Set(['work','coding','calendar']),
  integrations: new Set(['google','github']),
  proactivity: 'Suggest actions',
};

// ---------- ONBOARDING WIZARD ----------
let currentStep = 0;
const totalSteps = 5;
function showStep(n){
  document.querySelectorAll('.wiz-step').forEach(s=>{
    s.style.display = (parseInt(s.dataset.step)===n) ? 'flex' : 'none';
  });
  document.querySelectorAll('.step-dot').forEach(d=>{
    d.classList.toggle('done', parseInt(d.dataset.step) <= n);
  });
  currentStep = n;

  if (n === 1) {
    const btn = document.querySelector('.wiz-card[data-step="1"] .wiz-next');
    btn.disabled = true;
    btn.textContent = "Scanning...";
    fetch('/api/scan').then(res => res.json()).then(data => {
      const hw = data.hardware || {};
      const env = data.os_environment || {};
      const models = data.models || [];
      
      const rows = document.querySelectorAll('.wiz-card[data-step="1"] .detect-row .check-badge');
      if (rows.length >= 4) {
        rows[0].innerHTML = hw.gpu_model ? `✓ ${hw.gpu_model} — ${hw.vram_gb} GB VRAM` : `✓ CPU Only`;
        rows[1].innerHTML = `✓ ${hw.ram_gb} GB RAM`;
        rows[2].innerHTML = env.docker_running ? `✓ Connected` : `⚠ Not running`;
        rows[3].innerHTML = `✓ Reachable — ${models.length} models`;
      }
      btn.textContent = "Continue →";
      btn.disabled = false;
    }).catch(e => {
      console.error(e);
      btn.textContent = "Continue →";
      btn.disabled = false;
    });
  }
}
document.querySelectorAll('.wiz-next').forEach(b=>b.addEventListener('click', ()=>{
  if(currentStep < totalSteps-1) {
    showStep(currentStep+1);
  } else { 
    applyPersonalization(); 
    
    // Save setup
    const mode = document.querySelector('.wiz-card[data-step="2"] .opt-card.selected').dataset.mode;
    const theme = document.documentElement.getAttribute('data-theme');
    
    fetch('/api/setup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        mode: mode,
        theme: theme,
        integrations: Array.from(appState.integrations),
        focus: Array.from(appState.focusAreas)
      })
    }).then(() => {
      navigateTo('dashboard'); 
    }).catch(console.error);
  }
}));
document.querySelectorAll('.wiz-back').forEach(b=>b.addEventListener('click', ()=>{
  if(currentStep > 0) showStep(currentStep-1);
}));
function navigateTo(screen){
  document.querySelector(`.nav-item[data-screen="${screen}"]`).click();
}

// opt-card multi-select toggles (focus areas)
document.querySelectorAll('.opt-card[data-toggle]').forEach(c=>{
  c.addEventListener('click', ()=>{
    c.classList.toggle('selected');
    const focus = c.dataset.focus;
    if(!focus) return;
    if(c.classList.contains('selected')) appState.focusAreas.add(focus);
    else appState.focusAreas.delete(focus);
  });
});

// switches (generic on/off; onboarding integration switches also update state)
document.querySelectorAll('.switch[data-switch]').forEach(s=>{
  s.addEventListener('click', ()=>{
    s.classList.toggle('on');
    const integ = s.dataset.integration;
    if(!integ) return;
    if(s.classList.contains('on')) appState.integrations.add(integ);
    else appState.integrations.delete(integ);
  });
});

// segmented controls (the proactivity control in onboarding also updates state)
document.querySelectorAll('.seg').forEach(seg=>{
  seg.querySelectorAll('button').forEach(btn=>{
    btn.addEventListener('click', ()=>{
      seg.querySelectorAll('button').forEach(b=>b.classList.remove('active'));
      btn.classList.add('active');
      if(seg.closest('.wiz-step')) appState.proactivity = btn.textContent;
    });
  });
});

// ---------- APPLY PERSONALIZATION (runs once onboarding finishes) ----------
function applyPersonalization(){
  // Dashboard suggestion chips: highlight the ones matching chosen focus areas
  document.querySelectorAll('#suggest-row .suggest-chip').forEach(chip=>{
    chip.classList.toggle('chip-match', appState.focusAreas.has(chip.dataset.focus));
  });

  // Skills marketplace: badge + float matching skills to the top
  const grid = document.getElementById('skills-grid');
  const cards = Array.from(grid.querySelectorAll('.skill-card'));
  cards.forEach(card=>{
    card.classList.toggle('suggested', appState.focusAreas.has(card.dataset.focus));
  });
  cards.sort((a,b)=> (b.classList.contains('suggested')?1:0) - (a.classList.contains('suggested')?1:0));
  cards.forEach(c=> grid.appendChild(c));

  // Integrations screen: mirror what was connected during setup
  document.querySelectorAll('.int-item[data-int]').forEach(item=>{
    const connected = appState.integrations.has(item.dataset.int);
    const statusSlot = item.querySelector('.pill, .btn');
    if(!statusSlot) return;
    if(connected){
      const pill = document.createElement('span');
      pill.className = 'pill on';
      pill.textContent = 'Connected';
      statusSlot.replaceWith(pill);
    }
  });

  // Settings: mirror chosen proactivity level
  const settingsProactivitySeg = document.querySelectorAll('#screen-settings .seg')[1];
  if(settingsProactivitySeg){
    settingsProactivitySeg.querySelectorAll('button').forEach(b=>{
      b.classList.toggle('active', b.textContent === appState.proactivity);
    });
  }
}

// ---------- PERMISSIONS CYCLING ----------
const permLevels = ['ask','suggest','auto','off'];
const permLabel = { ask:'ASK', suggest:'SUG', auto:'AUTO', off:'OFF' };
document.querySelectorAll('.perm-cell[data-cycle]').forEach(cell=>{
  cell.addEventListener('click', ()=>{
    let cur = permLevels.find(l=>cell.classList.contains(l));
    let idx = (permLevels.indexOf(cur)+1) % permLevels.length;
    permLevels.forEach(l=>cell.classList.remove(l));
    cell.classList.add(permLevels[idx]);
    cell.textContent = permLabel[permLevels[idx]];
  });
});

// ---------- SKILLS GRID ----------
const SKILLS = [
  {icon:'🔍', name:'Deep Research', desc:'Multi-step web research with cited summaries.', installed:true, focus:'research'},
  {icon:'📁', name:'File Organizer', desc:'Sorts, renames and dedupes local files.', installed:true, focus:'files'},
  {icon:'💻', name:'Coding Assistant', desc:'Reads repos, opens PRs, runs tests.', installed:false, focus:'coding'},
  {icon:'📧', name:'Email Assistant', desc:'Drafts, summarizes, and triages inbox.', installed:true, focus:'work'},
  {icon:'📅', name:'Calendar Manager', desc:'Books meetings, resolves conflicts.', installed:false, focus:'calendar'},
  {icon:'📊', name:'Excel Analyst', desc:'Cleans data and builds pivot summaries.', installed:false, focus:'work'},
  {icon:'🧾', name:'Invoice Processor', desc:'Extracts line items from PDFs.', installed:false, focus:'files'},
  {icon:'🌐', name:'Website Monitor', desc:'Watches pages for price or content changes.', installed:true, focus:'automation'},
  {icon:'📝', name:'Meeting Summarizer', desc:'Turns transcripts into action items.', installed:false, focus:'calendar'},
];
document.getElementById('skills-grid').innerHTML = SKILLS.map((s,i)=>`
  <div class="card skill-card" data-focus="${s.focus}">
    <div class="skill-icon">${s.icon}</div>
    <span class="suggested-badge">Suggested for you</span>
    <h4>${s.name}</h4>
    <p>${s.desc}</p>
    <div class="skill-foot">
      <span class="stars">★★★★☆</span>
      <button class="btn sm ${s.installed?'ghost':''}" data-install="${i}">${s.installed?'Installed ✓':'Install'}</button>
    </div>
  </div>`).join('');
document.querySelectorAll('[data-install]').forEach(btn=>{
  btn.addEventListener('click', ()=>{
    const installed = btn.textContent.includes('Installed');
    btn.textContent = installed ? 'Install' : 'Installed ✓';
    btn.classList.toggle('ghost');
  });
});

// ---------- CHAT ----------
const chatLog = document.getElementById('chat-log');
const chatInput = document.getElementById('chat-input');
async function sendChat(){
  const val = chatInput.value.trim();
  if(!val) return;
  const userMsg = document.createElement('div');
  userMsg.className = 'msg user';
  userMsg.textContent = val;
  chatLog.appendChild(userMsg);
  chatInput.value = '';
  chatLog.scrollTop = chatLog.scrollHeight;
  
  try {
    const res = await fetch('/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ task: val })
    });
    const data = await res.json();
    
    const agentMsg = document.createElement('div');
    agentMsg.className = 'msg agent';
    agentMsg.innerHTML = "Got it — sending task to runtime... <div class='action-card'>Status: " + data.status + "</div>";
    chatLog.appendChild(agentMsg);
    chatLog.scrollTop = chatLog.scrollHeight;
  } catch (e) {
    console.error(e);
  }
}
document.getElementById('chat-send').addEventListener('click', sendChat);
chatInput.addEventListener('keydown', e=>{ if(e.key==='Enter') sendChat(); });

// ---------- EXECUTION PROFILE RESOLVER ----------
const resolveBtn = document.getElementById('profile-resolve-btn');
if (resolveBtn) {
  resolveBtn.addEventListener('click', async () => {
    const taskInput = document.getElementById('profile-task-input').value;
    if(!taskInput) return;
    resolveBtn.disabled = true;
    resolveBtn.textContent = "Resolving...";
    
    try {
      const res = await fetch('/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task: taskInput })
      });
      const data = await res.json();
      
      if(res.ok) {
        document.querySelector('#profile-result .display').innerHTML = `${data.runtime} <span style="color:var(--text-faint); font-weight:400; font-size:14px;">+</span> <span style="font-family:var(--font-mono); font-size:16px;">${data.model}</span>`;
        document.querySelector('#profile-result .pill').textContent = data.suitability_status;
        document.querySelector('#profile-result .pill').style.background = data.is_verified ? 'var(--good)' : 'var(--warn)';
        
        const statCards = document.querySelectorAll('#profile-result .g3 .card div:nth-child(2)');
        if(statCards.length >= 3) {
          statCards[0].textContent = data.mode;
          statCards[1].textContent = data.is_verified ? `${data.confidence_score}% empirical` : `UNKNOWN (0% empirical)`;
          statCards[1].style.color = data.is_verified ? 'var(--good)' : 'var(--warn)';
          statCards[2].textContent = `$${data.estimated_cost} / 1M tokens`;
        }
        
        const reasonsContainer = document.querySelector('#profile-result > div:nth-child(4)');
        if (reasonsContainer) {
          reasonsContainer.innerHTML = data.explainability.map(reason => {
            const isWarn = reason.includes('[WARN]');
            const text = reason.replace('[WARN]', '').replace('[PASS]', '').trim();
            return `<div class="reason-row ${isWarn ? 'warn' : 'pass'}"><i data-lucide="${isWarn ? 'alert-triangle' : 'check-circle-2'}"></i><span>${text}</span></div>`;
          }).join('');
          lucide.createIcons();
        }
        
        const altContainer = document.querySelector('#profile-result > div:last-child');
        if (data.alternatives && data.alternatives.length > 0) {
          altContainer.innerHTML = `<div style="font-size:13px; color:var(--text-dim);">Alternative: <span style="font-family:var(--font-mono); color:var(--text);">${data.alternatives[0].model}</span> (${data.alternatives[0].mode})</div><div style="font-size:11.5px; color:var(--text-faint);">Resolved just now</div>`;
        } else {
          altContainer.innerHTML = `<div style="font-size:13px; color:var(--text-dim);">No alternatives found</div><div style="font-size:11.5px; color:var(--text-faint);">Resolved just now</div>`;
        }
      } else {
        alert(data.error || "No suitable profile found");
      }
    } catch(e) {
      console.error(e);
    } finally {
      resolveBtn.disabled = false;
      resolveBtn.textContent = "Resolve";
    }
  });
}

// ---------- DIAGNOSTICS ----------
async function refreshDiagnostics() {
  const container = document.querySelector('#screen-diagnostics .card:first-child');
  if(!container) return;
  
  try {
    const res = await fetch('/api/doctor');
    const data = await res.json();
    
    if(res.ok && data.diagnostics) {
      // Remove old diagnostic rows, keep header
      const rows = container.querySelectorAll('.diag-row');
      rows.forEach(r => r.remove());
      
      data.diagnostics.forEach(diag => {
        const isPass = diag.status === 'PASS';
        const isWarn = diag.status === 'WARN';
        const isFail = diag.status === 'FAIL';
        const cssClass = isPass ? 'pass' : (isWarn ? 'warn' : 'fail');
        const icon = isPass ? 'check-circle-2' : (isWarn ? 'alert-triangle' : 'x-circle');
        
        const div = document.createElement('div');
        div.className = `diag-row ${cssClass}`;
        div.innerHTML = `<i data-lucide="${icon}"></i><div class="dr-body"><div class="dr-t">${diag.check}</div><div class="dr-s">${diag.message}</div></div>`;
        container.appendChild(div);
      });
      lucide.createIcons();
    }
  } catch(e) {
    console.error(e);
  }
}
document.querySelector('.nav-item[data-screen="diagnostics"]').addEventListener('click', refreshDiagnostics);