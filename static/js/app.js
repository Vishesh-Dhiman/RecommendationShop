/* ================================================================
   ShopDesi — Main App JS
   Pure fetch() API, no Jinja2 logic
================================================================ */

// ── State ────────────────────────────────────────────────────────
const S = {
  user: null, cartIds: [], categories: {}
};

// ── Init (runs on every page) ─────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  await initUser();
  if (window._pageInit) window._pageInit();
});

async function initUser() {
  try {
    const r = await fetch('/api/me');
    if (!r.ok) return;
    S.user = await r.json();
    if (S.user.error) { S.user = null; return; }
    S.cartIds = S.user.cart || [];
    renderNavUser(S.user);
    updateCartBadge(S.cartIds.length);
    loadNavCategories();
  } catch(e) {}
}

function renderNavUser(u) {
  const wrap = document.getElementById('nav-user-wrap');
  const av   = document.getElementById('nav-avatar');
  if (!wrap || !av) return;
  wrap.style.display = '';
  av.textContent = u.avatar || u.name.charAt(0);
  const nm = document.getElementById('um-name');
  const un = document.getElementById('um-uname');
  if (nm) nm.textContent = u.name;
  if (un) un.textContent = '@' + u.username;
  // Prefill search if query in URL
  const q = new URLSearchParams(location.search).get('q');
  const si = document.getElementById('nav-q');
  if (q && si) si.value = q;
}

async function loadNavCategories() {
  try {
    const r  = await fetch('/api/products?page=1');
    const d  = await r.json();
    S.categories = d.categories || {};
    renderCatBar(S.categories);
  } catch(e) {}
}

function renderCatBar(cats, active='') {
  const el = document.getElementById('cat-bar');
  if (!el) return;
  const param = new URLSearchParams(location.search).get('category') || active;
  let html = `<a href="/" class="cat-link ${!param?'active':''}">All</a>`;
  Object.keys(cats).forEach(cat => {
    const a = cat === param ? 'active' : '';
    html += `<a href="/?category=${enc(cat)}" class="cat-link ${a}">${cat}</a>`;
  });
  el.innerHTML = html;
}

// ── Nav search ────────────────────────────────────────────────────
function navSearch(e) {
  e.preventDefault();
  const q = document.getElementById('nav-q').value.trim();
  if (q) location.href = '/search?q=' + enc(q);
}

// ── Cart badge ─────────────────────────────────────────────────────
function updateCartBadge(n) {
  document.querySelectorAll('#nav-cart-count,.cart-badge').forEach(el => {
    el.textContent = n;
    el.classList.toggle('has-items', n > 0);
  });
}

// ── Cart toggle ────────────────────────────────────────────────────
async function toggleCart(pid, btn) {
  if (!btn) return;
  btn.disabled = true;
  try {
    const r = await fetch('/api/cart/toggle', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({product_id: pid})
    });
    const d = await r.json();
    if (d.error) { toast(d.error, 'error'); return; }
    S.cartIds = d.cart_ids || [];
    updateCartBadge(d.cart_count);
    const added = d.action === 'added';
    toast(added ? '🛒 Added to cart!' : 'Removed from cart', added ? 'success' : 'info');
    // Update ALL cart buttons for this product on page
    document.querySelectorAll(`[data-cart-pid="${pid}"]`).forEach(b => {
      b.textContent = added ? '✓ Added' : '+ Cart';
      b.classList.toggle('in-cart', added);
    });
  } finally { btn.disabled = false; }
}

// ── Product card ───────────────────────────────────────────────────
function card(p, cartIds = [], infoLabel = '') {
  const inCart   = (cartIds || S.cartIds).includes(p.id);
  const rClass   = p.rating >= 4.3 ? 'r-green' : p.rating >= 3.8 ? 'r-orange' : 'r-red';
  const discBadge= p.discount > 0 ? `<span class="disc-badge">${p.discount}% off</span>` : '';
  const mrpHtml  = p.mrp > p.price
    ? `<span class="card-mrp">₹${fmt(p.mrp)}</span><span class="card-save">${p.discount}% off</span>` : '';
  const infoBadge= infoLabel
    ? `<span class="info-badge" title="${infoLabel}">ℹ️</span>` : '';
  return `
<div class="card" onclick="location.href='/product/${p.id}'">
  <div class="card-img" style="background:${p.color_hex}">
    <div class="card-img-center">
      <div class="card-img-cat">${p.subcategory}</div>
      <div class="card-img-brand">${p.brand}</div>
    </div>
    ${discBadge}${infoBadge}
  </div>
  <div class="card-body">
    <div class="card-brand">${p.brand}</div>
    <div class="card-name">${p.name}</div>
    <div class="card-row">
      <span class="rating-pill ${rClass}">${p.rating} ★</span>
      <span class="card-reviews">${fmtN(p.reviews)}</span>
    </div>
    <div class="card-row">
      <span class="card-price">₹${fmt(p.price)}</span>${mrpHtml}
    </div>
    <button class="cart-btn ${inCart?'in-cart':''}" data-cart-pid="${p.id}"
      onclick="event.stopPropagation();toggleCart(${p.id},this)">
      ${inCart ? '✓ Added' : '+ Cart'}
    </button>
  </div>
</div>`;
}

// ── Strip renderer ─────────────────────────────────────────────────
function renderStrip(id, products, cartIds, title, tag, infoText) {
  const el = document.getElementById(id);
  if (!el) return;
  if (!products || !products.length) { el.style.display = 'none'; return; }
  el.style.display = '';
  const tagHtml  = tag ? `<span class="strip-tag">${tag}</span>` : '';
  const infoHtml = infoText
    ? `<span class="strip-info-btn" onclick="event.stopPropagation();showInfo('${id}-info','${infoText.replace(/'/g,"\\'")}')" title="How this works">ℹ️</span>` : '';
  el.innerHTML = `
    <div class="strip-head">
      <h3>${title}</h3>${tagHtml}${infoHtml}
    </div>
    <div class="info-popup" id="${id}-info" style="display:none">
      <span>${infoText||''}</span>
      <button onclick="document.getElementById('${id}-info').style.display='none'">✕</button>
    </div>
    <div class="strip-scroll" id="${id}-scroll">
      ${products.map(p => card(p, cartIds)).join('')}
    </div>`;
  dragScroll(document.getElementById(id + '-scroll'));
}

// ── Info popup ─────────────────────────────────────────────────────
function showInfo(id, text) {
  const el = document.getElementById(id);
  if (!el) return;
  el.style.display = el.style.display === 'none' ? 'flex' : 'none';
}

// ── Grid renderer ──────────────────────────────────────────────────
function renderGrid(id, products, cartIds) {
  const el = document.getElementById(id);
  if (!el) return;
  if (!products || !products.length) {
    el.innerHTML = `<div class="empty-grid">
      <div style="font-size:40px">🔍</div>
      <h4>No products found</h4>
      <p><a href="/">Clear filters</a> and try again.</p>
    </div>`; return;
  }
  el.innerHTML = products.map(p => card(p, cartIds)).join('');
}

// ── Pagination ──────────────────────────────────────────────────────
function renderPagination(id, page, total, fn) {
  const el = document.getElementById(id);
  if (!el || total <= 1) { if(el) el.innerHTML=''; return; }
  let h = '';
  if (page > 1) h += btn(fn, page-1, '‹ Prev');
  for (let i=1; i<=total; i++) {
    if (i===page) h += `<span class="pg active">${i}</span>`;
    else if (i<=2||i>total-2||(i>=page-2&&i<=page+2)) h += btn(fn, i, i);
    else if (i===3||i===total-2) h += `<span class="pg">…</span>`;
  }
  if (page < total) h += btn(fn, page+1, 'Next ›');
  el.innerHTML = h;
}
const btn = (fn, p, lbl) =>
  `<button class="pg" onclick="${fn}(${p})">${lbl}</button>`;

// ── Skeleton ────────────────────────────────────────────────────────
function skeleton(n = 10) {
  return `<div class="skel-grid">${
    Array(n).fill(`<div class="skel-card">
      <div class="skel-img skel"></div>
      <div class="skel-line skel w70"></div>
      <div class="skel-line skel w50"></div>
      <div class="skel-line skel w40"></div>
    </div>`).join('')
  }</div>`;
}

// ── Drag scroll ─────────────────────────────────────────────────────
function dragScroll(el) {
  if (!el) return;
  let down=false, sx, sl;
  el.addEventListener('mousedown', e=>{down=true;sx=e.pageX-el.offsetLeft;sl=el.scrollLeft;el.style.cursor='grabbing'});
  ['mouseleave','mouseup'].forEach(ev=>el.addEventListener(ev,()=>{down=false;el.style.cursor=''}));
  el.addEventListener('mousemove', e=>{if(!down)return;e.preventDefault();el.scrollLeft=sl-(e.pageX-el.offsetLeft-sx)*1.2});
}

// ── Toast ────────────────────────────────────────────────────────────
let _tt;
function toast(msg, type='info', dur=2600) {
  const el = document.getElementById('toast');
  if (!el) return;
  const icons = {success:'✅',error:'❌',warn:'⚠️',info:'ℹ️'};
  el.innerHTML = `<span>${icons[type]||'ℹ️'} ${msg}</span>`;
  el.className = `toast-wrap show ${type}`;
  clearTimeout(_tt);
  _tt = setTimeout(()=>el.classList.remove('show'), dur);
}

// ── Helpers ──────────────────────────────────────────────────────────
const fmt  = n => Number(n).toLocaleString('en-IN');
const fmtN = n => Number(n).toLocaleString('en-IN');
const enc  = s => encodeURIComponent(s);

// ── Dropdown ─────────────────────────────────────────────────────────
function toggleUserMenu() {
  document.getElementById('user-menu')?.classList.toggle('open');
}
function closeMenus() {
  document.getElementById('user-menu')?.classList.remove('open');
}
document.addEventListener('click', e => {
  const wrap = document.getElementById('nav-user-wrap');
  if (wrap && !wrap.contains(e.target)) closeMenus();
});
