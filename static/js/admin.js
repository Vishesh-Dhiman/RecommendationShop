// ShopDesi Admin JS
let _allProds = [], _stats = {}, _users = [];
const DEMO_UIDS = ['u1','u2','u3','u4','u5','u6','u7','u8'];

window.addEventListener('DOMContentLoaded', () => {
  showTab(document.querySelector('.anl.active'), 'dashboard');
});

function showTab(el, tab) {
  document.querySelectorAll('.atab').forEach(t => t.style.display = 'none');
  document.querySelectorAll('.anl').forEach(l => l.classList.remove('active'));
  document.getElementById('tab-' + tab).style.display = '';
  if (el) el.classList.add('active');
  const loaders = { dashboard: loadDashboard, users: loadUsers, products: () => { loadAdminProducts(); loadCatFilter(); }, ml: loadML, settings: loadSettings };
  if (loaders[tab]) loaders[tab]();
}

const COLORS = ['#2874f0','#388e3c','#fb641b','#9c27b0','#f39c12','#e53935','#00bcd4','#607d8b'];
const INR = n => '₹' + Number(n).toLocaleString('en-IN');

// ── Dashboard ──────────────────────────────────────────────────────
async function loadDashboard() {
  const r = await fetch('/api/admin/stats');
  _stats  = await r.json();
  const cards = [
    {icon:'📦',val:_stats.total_products,  lbl:'Products'},
    {icon:'👥',val:_stats.total_users,     lbl:'Users'},
    {icon:'👁️',val:_stats.total_views,    lbl:'Total Views'},
    {icon:'🛒',val:_stats.total_cart,      lbl:'In Carts'},
    {icon:'✅',val:_stats.total_purchases, lbl:'Purchases'},
    {icon:'🔍',val:_stats.total_searches,  lbl:'Searches'},
  ];
  document.getElementById('dash-stats').innerHTML = cards.map(c =>
    `<div class="a-stat-card">
      <div class="a-stat-icon">${c.icon}</div>
      <div class="a-stat-val">${Number(c.val).toLocaleString('en-IN')}</div>
      <div class="a-stat-lbl">${c.lbl}</div>
    </div>`).join('');
  drawDonut('chart-cat-dist', _stats.category_counts || {});
  drawBarH('chart-interests', _stats.interest_counts || {}, '#9c27b0');
  drawBarH('chart-cat-views', _stats.cat_view_totals || {}, '#2874f0');
  const tv = _stats.top_viewed || [];
  document.getElementById('dash-top-viewed').innerHTML = tv.length
    ? `<table class="a-table"><thead><tr><th>Rank</th><th>Product</th><th>Category</th><th>Price</th><th>Views</th></tr></thead><tbody>
      ${tv.map((item,i)=>`<tr>
        <td><strong>#${i+1}</strong></td>
        <td>${item.product.name}</td>
        <td><span class="cat-chip">${item.product.category}</span></td>
        <td>${INR(item.product.price)}</td>
        <td><span class="view-badge">${item.count}</span></td>
      </tr>`).join('')}</tbody></table>`
    : '<p class="a-hint" style="padding:12px">No views recorded yet. Ask users to browse!</p>';
}

// ── Canvas Charts ───────────────────────────────────────────────────
function drawDonut(canvasId, data) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height, cx = W/2, cy = H/2;
  const r = Math.min(W,H)/2 - 30, ir = r * 0.55;
  const entries = Object.entries(data);
  const total = entries.reduce((s,[,v])=>s+v,0);
  ctx.clearRect(0,0,W,H);
  let angle = -Math.PI/2;
  entries.forEach(([label,val],i) => {
    const slice = (val/total)*2*Math.PI;
    ctx.beginPath(); ctx.moveTo(cx,cy); ctx.arc(cx,cy,r,angle,angle+slice); ctx.closePath();
    ctx.fillStyle = COLORS[i%COLORS.length]; ctx.fill();
    const midA = angle+slice/2, lx=cx+(r+18)*Math.cos(midA), ly=cy+(r+18)*Math.sin(midA);
    ctx.font='11px Segoe UI'; ctx.fillStyle='#424242';
    ctx.textAlign=lx>cx?'left':'right'; ctx.fillText(`${label}: ${val}`,lx,ly);
    angle += slice;
  });
  ctx.beginPath(); ctx.arc(cx,cy,ir,0,2*Math.PI); ctx.fillStyle='#fff'; ctx.fill();
  ctx.font='bold 13px Segoe UI'; ctx.fillStyle='#212121'; ctx.textAlign='center'; ctx.textBaseline='middle';
  ctx.fillText(`${total} total`, cx, cy);
}

function drawBarH(containerId, data, color='#2874f0') {
  const el = document.getElementById(containerId);
  if (!el) return;
  const entries = Object.entries(data).sort((a,b)=>b[1]-a[1]);
  if (!entries.length) { el.innerHTML='<p class="a-hint" style="padding:12px">No data yet</p>'; return; }
  const maxVal = entries[0][1]||1;
  el.innerHTML = entries.map(([label,val]) => {
    const pct = Math.round(val/maxVal*100);
    return `<div class="hbar-row">
      <div class="hbar-label">${label}</div>
      <div class="hbar-track"><div class="hbar-fill" style="width:${pct}%;background:${color}">${val}</div></div>
    </div>`;
  }).join('');
}

function drawGroupedBar(containerId, users, categories) {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = `
    <div class="gb-chart">
      ${users.map((u,ui) => `
        <div class="gb-user">
          <div class="gb-uname">${u.name}</div>
          <div class="gb-bars">
            ${categories.map((cat,ci) => {
              const score = u.scores[cat]||0, maxS=30, pct=Math.min(100,Math.round(score/maxS*100));
              return `<div class="gb-bar-wrap" title="${cat}: ${score.toFixed(1)}">
                <div class="gb-bar" style="height:${pct}%;background:${COLORS[ci%COLORS.length]}"></div>
                <div class="gb-bar-val">${score>0?score.toFixed(0):''}</div>
              </div>`;
            }).join('')}
          </div>
        </div>`).join('')}
    </div>
    <div class="gb-legend">
      ${categories.map((cat,i)=>
        `<span class="gb-leg-item"><span class="gb-leg-dot" style="background:${COLORS[i%COLORS.length]}"></span>${cat}</span>`
      ).join('')}
    </div>`;
}

// ── Users ────────────────────────────────────────────────────────────
async function loadUsers() {
  const r = await fetch('/api/admin/users');
  _users  = await r.json();
  const cats = Object.keys(_stats.category_counts||{});
  drawBarH('chart-user-interactions',
    Object.fromEntries(_users.map(u=>[u.name.split(' ')[0], u.total_interactions])), '#fb641b');
  drawGroupedBar('chart-user-interests-detail',
    _users.map(u=>({name:u.name.split(' ')[0], scores:u.interest_scores||{}})), cats.slice(0,6));

  document.getElementById('users-list').innerHTML = _users.map(u => `
    <div class="a-card mb-10">
      <div class="u-card-top">
        <div class="u-avatar">${u.name.charAt(0)}</div>
        <div class="u-info">
          <div class="u-name">${u.name}
            <span class="u-uname">@${u.username}</span>
            ${!DEMO_UIDS.includes(u.id)?'<span class="u-new-badge">NEW</span>':''}
          </div>
          <div class="u-ints">
            ${(u.interests||[]).map(i=>`<span class="u-int">${i}</span>`).join('')||
              '<span style="color:var(--text-muted);font-size:11px">No interests yet</span>'}
          </div>
        </div>
        <div class="u-stats-row">
          <div class="u-stat"><div class="u-stat-n">${u.viewed_count}</div><div class="u-stat-l">Views</div></div>
          <div class="u-stat"><div class="u-stat-n">${u.cart_count}</div><div class="u-stat-l">Cart</div></div>
          <div class="u-stat"><div class="u-stat-n">${u.purchase_count}</div><div class="u-stat-l">Buys</div></div>
          <div class="u-stat"><div class="u-stat-n">${u.search_count}</div><div class="u-stat-l">Searches</div></div>
        </div>
      </div>
      ${Object.keys(u.category_views||{}).length?`
        <div class="cv-row">
          ${Object.entries(u.category_views).map(([cat,cnt])=>
            `<span class="cv-chip ${cnt>=3?'done':''}">${cat}: ${cnt}</span>`).join('')}
        </div>`:''}
      <div class="u-actions">
        <button class="btn-sm" onclick="adminReset('${u.id}','reset_history')">Reset History</button>
        <button class="btn-sm" onclick="adminReset('${u.id}','reset_cart')">Reset Cart</button>
        <button class="btn-sm" onclick="adminReset('${u.id}','reset_purchases')">Reset Purchases</button>
        <button class="btn-sm danger" onclick="adminReset('${u.id}','reset_all')">Reset All</button>
        ${!DEMO_UIDS.includes(u.id)
          ? `<button class="btn-sm delete" onclick="deleteUser('${u.id}','${u.name}')">🗑 Delete</button>`
          : ''}
      </div>
    </div>`).join('');
}

async function deleteUser(uid, name) {
  if(!confirm(`Delete user "${name}"?\nThis cannot be undone.`)) return;
  const r = await fetch(`/api/admin/users/${uid}`, {method:'DELETE'});
  const d = await r.json();
  if(d.ok){ toast('Deleted: '+name,'success'); loadUsers(); }
  else toast(d.error||'Error','error');
}

async function adminReset(uid, action) {
  if(!confirm('Reset this user data?')) return;
  const r = await fetch(`/api/admin/users/${uid}`,{method:'PATCH',
    headers:{'Content-Type':'application/json'}, body:JSON.stringify({[action]:true})});
  const d = await r.json();
  if(d.ok){toast('Done!','success'); loadUsers();}
}

async function bulkReset(type) {
  if(!confirm(`Reset ${type} for ALL users? Cannot be undone.`)) return;
  const r = await fetch('/api/admin/users');
  const us = await r.json();
  const key = {history:'reset_history',cart:'reset_cart',interests:'interests',all:'reset_all'}[type];
  for(const u of us) {
    const body = type==='interests'?{interests:[]}:{[key]:true};
    await fetch(`/api/admin/users/${u.id}`,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  }
  toast(`All users ${type} reset!`,'success'); loadUsers();
}

const DEFAULT_INTERESTS = {
  u1:['Electronics','Books'], u2:['Fashion','Beauty & Personal Care'],
  u3:['Sports & Fitness','Electronics'], u4:['Home & Kitchen','Beauty & Personal Care'],
  u5:['Electronics','Sports & Fitness'], u6:['Books','Fashion'],
  u7:['Electronics','Fashion','Books'],  u8:['Beauty & Personal Care','Fashion'],
};

async function bulkSetDefault() {
  if(!confirm('Set all demo users to default state?\n• Clear activity\n• Restore original interests')) return;
  const r = await fetch('/api/admin/users');
  const us = await r.json();
  for(const u of us) {
    await fetch(`/api/admin/users/${u.id}`,{method:'PATCH',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({reset_all:true, interests: DEFAULT_INTERESTS[u.id]||[]})});
  }
  toast('All users set to default!','success'); loadUsers();
}

// ── Products ────────────────────────────────────────────────────────
async function loadAdminProducts() {
  const cat = document.getElementById('prod-cat')?.value||'';
  const r   = await fetch('/api/admin/products'+(cat?'?category='+encodeURIComponent(cat):''));
  _allProds = await r.json(); renderProds(_allProds);
}
function renderProds(prods) {
  document.getElementById('prod-count').textContent = prods.length+' products';
  document.getElementById('prod-tbody').innerHTML = prods.map(p=>`
    <tr>
      <td>#${p.id}</td>
      <td><strong>${p.name}</strong></td>
      <td>${p.brand}</td>
      <td><span class="cat-chip">${p.category}</span></td>
      <td>${p.subcategory}</td>
      <td>${INR(p.price)}</td>
      <td><span style="color:#9e9e9e">${INR(p.mrp)}</span></td>
      <td>${p.discount>0?`<span style="color:#fb641b;font-weight:700">${p.discount}%</span>`:'—'}</td>
      <td><span class="r-chip" style="background:${p.rating>=4.3?'#388e3c':p.rating>=3.8?'#ff9800':'#e53935'}">${p.rating}★</span></td>
      <td>${Number(p.reviews).toLocaleString('en-IN')}</td>
      <td>${Number(p.popularity).toLocaleString('en-IN')}</td>
    </tr>`).join('');
}
function filterProdsLocal() {
  const q = document.getElementById('prod-q').value.toLowerCase();
  renderProds(_allProds.filter(p=>p.name.toLowerCase().includes(q)||p.brand.toLowerCase().includes(q)));
}
async function loadCatFilter() {
  const r=await fetch('/api/admin/stats'); const d=await r.json();
  const sel=document.getElementById('prod-cat'); if(!sel) return;
  sel.innerHTML='<option value="">All Categories</option>'+
    (d.categories||[]).map(c=>`<option value="${c}">${c}</option>`).join('');
}
function loadProducts() { loadAdminProducts(); }

// ── ML ──────────────────────────────────────────────────────────────
async function loadML(){
  const r=await fetch('/api/admin/stats'); const d=await r.json();
  const ts=d.training_stats||{};
  document.getElementById('ml-stats').innerHTML = ts.trained_at?`
    <div class="ml-stat-grid">
      <div class="ml-stat"><div class="ml-stat-v">${ts.trained_at}</div><div class="ml-stat-l">Last Trained</div></div>
      <div class="ml-stat"><div class="ml-stat-v">${ts.elapsed_sec}s</div><div class="ml-stat-l">Training Time</div></div>
      <div class="ml-stat"><div class="ml-stat-v">${ts.vocab_size}</div><div class="ml-stat-l">TF-IDF Vocab</div></div>
      <div class="ml-stat"><div class="ml-stat-v">${ts.cf_nonzero}</div><div class="ml-stat-l">CF Non-zero</div></div>
      <div class="ml-stat"><div class="ml-stat-v">${(ts.cf_sparsity*100).toFixed(1)}%</div><div class="ml-stat-l">CF Sparsity</div></div>
      <div class="ml-stat"><div class="ml-stat-v">${ts.product_count}</div><div class="ml-stat-l">Products</div></div>
    </div>` : '<p class="a-hint">Models not trained yet. Click Retrain.</p>';
  if(ts.weights){
    document.getElementById('weight-grid').innerHTML =
      Object.entries(ts.weights).map(([k,v])=>`
        <div class="weight-row">
          <span class="w-label">${k.charAt(0).toUpperCase()+k.slice(1)}</span>
          <div class="w-bar-track"><div class="w-bar" style="width:${Math.min(100,v/5*100)}%">${v}</div></div>
        </div>`).join('');
  }
  const sv=document.getElementById('thresh-slider'), tv=document.getElementById('thresh-val');
  if(sv){ sv.value=d.interest_threshold||3; tv.textContent=d.interest_threshold||3; }
}

async function retrain(){
  const btn=document.getElementById('retrain-btn');
  btn.textContent='⏳ Training…'; btn.disabled=true;
  const r=await fetch('/api/admin/retrain',{method:'POST'});
  const d=await r.json();
  btn.textContent='🔄 Retrain Models Now'; btn.disabled=false;
  if(d.ok){ toast(`Training done in ${d.stats.elapsed_sec}s!`,'success'); loadML(); }
}

async function saveThreshold(){
  const val=document.getElementById('thresh-slider').value;
  const r=await fetch('/api/admin/settings',{method:'POST',
    headers:{'Content-Type':'application/json'},body:JSON.stringify({interest_threshold:parseInt(val)})});
  const d=await r.json();
  if(d.ok) toast('Threshold updated to '+val,'success');
}

// ── Settings ─────────────────────────────────────────────────────────
async function loadSettings(){
  const r=await fetch('/api/admin/stats'); const d=await r.json();
  document.getElementById('sys-info').innerHTML=`
    <div class="sys-grid">
      <div class="sys-item"><span>Products</span><strong>${d.total_products}</strong></div>
      <div class="sys-item"><span>Users</span><strong>${d.total_users}</strong></div>
      <div class="sys-item"><span>Categories</span><strong>${(d.categories||[]).length}</strong></div>
      <div class="sys-item"><span>Interest Threshold</span><strong>${d.interest_threshold}</strong></div>
      <div class="sys-item"><span>Algorithm</span><strong>TF-IDF + CF + Interest</strong></div>
      <div class="sys-item"><span>Storage</span><strong>JSON + Pickle</strong></div>
      <div class="sys-item"><span>Backend</span><strong>Flask (Python)</strong></div>
      <div class="sys-item"><span>ML Models</span><strong>tfidf, cf, interest</strong></div>
    </div>`;
}
