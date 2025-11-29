// main_v2.js
async function fetchProducts(q='',brand='',sort=''){
  const url = new URL('/api/products', location.origin);
  if(q) url.searchParams.set('q', q);
  if(brand) url.searchParams.set('brand', brand);
  if(sort) url.searchParams.set('sort', sort);
  const res = await fetch(url);
  return res.json();
}
function el(tag, cls){ const e=document.createElement(tag); if(cls) e.className=cls; return e; }
async function renderProducts(){
  const q = document.getElementById('searchInput') ? document.getElementById('searchInput').value : '';
  const brand = document.getElementById('brandFilter') ? document.getElementById('brandFilter').value : '';
  const sort = document.getElementById('sortSelect') ? document.getElementById('sortSelect').value : '';
  const prods = await fetchProducts(q,brand,sort);
  const grid = document.getElementById('productsGrid');
  if(!grid) return;
  grid.innerHTML='';
  const brands = Array.from(new Set(prods.map(p=>p.brand))).sort();
  const bf = document.getElementById('brandFilter');
  if(bf && bf.children.length<=1){
    brands.forEach(b=>{
      const o=document.createElement('option'); o.value=b; o.textContent=b; bf.appendChild(o);
    });
  }
  prods.forEach(p=>{
    const card = el('div','card');
    const img = el('img'); img.src='/static/images/'+p.image; img.alt = p.name;
    card.appendChild(img);
    const h = el('h3'); h.textContent = p.name; card.appendChild(h);
    const br = el('div','brand-name'); br.textContent = p.brand + ' • Sizes: ' + (p.sizes || '-'); card.appendChild(br);
    const price = el('div','price'); price.textContent = '₹ '+parseFloat(p.price).toFixed(2); card.appendChild(price);
    const actions = el('div');
    const view = el('a'); view.href='/product/'+p.id; view.className='btn'; view.textContent='View';
    const add = el('button'); add.className='btn primary'; add.textContent='Add';
    add.onclick = async ()=>{ await addToCart(p.id,1); alert('Added to cart'); updateCartCount(); };
    const fav = el('button'); fav.className='btn'; fav.textContent='♡';
    fav.onclick = async ()=>{ await fetch('/api/fav/toggle',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:p.id})}); alert('Toggled favorite'); };
    actions.appendChild(view); actions.appendChild(add); actions.appendChild(fav);
    card.appendChild(actions);
    grid.appendChild(card);
  });
}
async function addToCart(id,qty){ await fetch('/api/cart/add', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({id,qty})}); }
async function updateCartCount(){ const res = await fetch('/api/cart'); const cart = await res.json(); let c=0; Object.values(cart).forEach(it=> c+=it.qty); const elc = document.getElementById('cartCount'); if(elc) elc.textContent = c; }
async function renderCart(){ const res = await fetch('/api/cart'); const cart = await res.json(); const container = document.getElementById('cartItems'); const summary = document.getElementById('cartSummary'); if(!container) return; container.innerHTML=''; let total=0; if(!cart || Object.keys(cart).length===0){ container.innerHTML='<p>Your cart is empty.</p>'; summary.innerHTML=''; return; } Object.values(cart).forEach(it=>{ const row = el('div','cart-item'); const img = el('img'); img.src='/static/images/'+it.image; const meta = el('div'); meta.innerHTML = '<strong>'+it.name+'</strong><div>₹ '+parseFloat(it.price).toFixed(2)+'</div>'; const qty = el('input'); qty.type='number'; qty.value=it.qty; qty.min=0; qty.style.width='60px'; qty.onchange = async ()=>{ await updateCart(it.id, parseInt(qty.value||0)); renderCart(); updateCartCount(); }; const remove = el('button'); remove.className='btn'; remove.textContent='Remove'; remove.onclick = async ()=>{ await updateCart(it.id,0); renderCart(); updateCartCount(); }; row.appendChild(img); row.appendChild(meta); row.appendChild(qty); row.appendChild(remove); container.appendChild(row); total += parseFloat(it.price)*parseInt(it.qty); }); summary.innerHTML = '<div class="cart-summary">Total: ₹ '+total.toFixed(2)+'</div>'; }
async function updateCart(id,qty){ await fetch('/api/cart/update',{method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({id,qty})}); }
window.addEventListener('DOMContentLoaded', ()=>{ const sb = document.getElementById('searchBtn'); if(sb) sb.addEventListener('click', renderProducts); const si = document.getElementById('searchInput'); if(si) si.addEventListener('keydown', e=>{ if(e.key==='Enter') renderProducts(); }); updateCartCount(); renderProducts(); });
