const API_BASE = "http://localhost:5000";

function qsel(s){return document.querySelector(s)}
function escapeHtml(str) {
  return str ? str.replace(/[&<>'\"]/g, t => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  }[t])) : "";
}

// === Funções principais ===

async function fetchProducts(){
  try{
    const res = await fetch(API_BASE + "/products");
    return res.ok ? res.json() : [];
  }catch(e){ console.error(e); return []; }
}

async function fetchOrders(){
  try{
    const res = await fetch(API_BASE + "/orders/");
    return res.ok ? res.json() : [];
  }catch(e){ console.error(e); return []; }
}

async function loadAll(){
  const [products, orders] = await Promise.all([fetchProducts(), fetchOrders()]);
  renderProducts(products);
  renderOrders(orders);
}

// === Renderização ===
function renderProducts(products){
  const tbody = qsel("#productsTable tbody");
  tbody.innerHTML = "";
  if(!products.length){
    tbody.innerHTML = "<tr><td colspan='4'><em>Nenhum produto encontrado</em></td></tr>";
    return;
  }

  products.forEach(p=>{
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${p.id}</td>
      <td>${escapeHtml(p.name)}</td>
      <td>${p.stock}</td>
      <td class="action-group">
        <button class="success sell-btn" data-id="${p.id}" data-name="${escapeHtml(p.name)}" data-stock="${p.stock}">Vender</button>
        <button class="primary add-btn" data-id="${p.id}">+ Estoque</button>
        <button class="danger del-btn" data-id="${p.id}">Remover</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function renderOrders(orders){
  const list = qsel("#ordersList");
  if(!orders.length){ list.innerHTML = "<small>Nenhum pedido</small>"; return; }
  list.innerHTML = orders.map(o=>`
    <div class="order">
      <b>#${o.id}</b> — ${escapeHtml(o.product_name)} (x${o.quantity})<br>
      <small>${o.created_at}</small>
    </div>
  `).join("");
}

// === Eventos ===
qsel("#refreshBtn").addEventListener("click", loadAll);

// Criar produto
qsel("#newProductBtn").addEventListener("click", async ()=>{
  const name = prompt("Nome do produto:");
  if(!name) return;
  const stock = prompt("Estoque inicial:", "0");
  try{
    const res = await fetch(API_BASE + "/admin/products/", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({name, stock: parseInt(stock)})
    });
    const data = await res.json();
    if(res.ok){
      alert("Produto criado com sucesso!");
      await loadAll();
    }else{
      alert(data.error || "Erro ao criar produto");
    }
  }catch(e){
    alert("Erro de rede: " + e.message);
  }
});

// Delegação de eventos na tabela
document.addEventListener("click", async ev=>{
  const target = ev.target;

  if(target.matches(".sell-btn")){
    openOrderModal(target.dataset);
  }

  if(target.matches(".add-btn")){
    const id = target.dataset.id;
    const qty = prompt("Quantidade a adicionar:");
    if(!qty) return;
    await updateStock(id, parseInt(qty), "add");
  }

  if(target.matches(".del-btn")){
    const id = target.dataset.id;
    if(confirm("Tem certeza que deseja remover este produto?")){
      await deleteProduct(id);
    }
  }
});

// === Funções administrativas ===
async function updateStock(id, qty, action){
  try{
    const res = await fetch(`${API_BASE}/admin/products/${id}`, {
      method: "PATCH",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({action, amount: qty})
    });
    const data = await res.json();
    if(res.ok){
      alert(`Estoque atualizado para ${data.new_stock}`);
      await loadAll();
    }else{
      alert(data.error || "Falha ao atualizar estoque");
    }
  }catch(e){
    alert("Erro de rede: " + e.message);
  }
}

async function deleteProduct(id){
  try{
    const res = await fetch(`${API_BASE}/admin/products/${id}`, {method:"DELETE"});
    const data = await res.json();
    if(res.ok){
      alert("Produto removido com sucesso!");
      await loadAll();
    }else{
      alert(data.error || "Erro ao remover produto");
    }
  }catch(e){
    alert("Erro de rede: " + e.message);
  }
}

// === Criar pedido (POST /orders) ===
const modal = qsel("#orderModal");
const modalProduct = qsel("#modalProduct");
const orderQty = qsel("#orderQty");
const modalMsg = qsel("#modalMsg");
let currentProductId = null;

function openOrderModal(data){
  currentProductId = data.id;
  modalProduct.textContent = `${data.name} — estoque disponível: ${data.stock}`;
  orderQty.value = 1;
  modalMsg.textContent = "";
  modal.classList.remove("hidden");
  modal.setAttribute("aria-hidden", "false");
}

qsel("#cancelOrder").addEventListener("click", ()=>{
  modal.classList.add("hidden");
  modal.setAttribute("aria-hidden", "true");
});

qsel("#submitOrder").addEventListener("click", async ()=>{
  const qty = parseInt(orderQty.value, 10);
  if(!qty || qty <= 0){
    showMsg("Quantidade inválida", "error");
    return;
  }
  try{
    const res = await fetch(API_BASE + "/orders/", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({productId: parseInt(currentProductId), quantity: qty})
    });
    const data = await res.json();
    if(res.status === 201){
      showMsg(`Pedido criado (#${data.orderId}).`, "success");
      await loadAll();
      setTimeout(()=> closeModal(), 1000);
    }else{
      showMsg(data.error || "Erro ao criar pedido", "error");
    }
  }catch(e){
    showMsg("Erro de rede: "+e.message, "error");
  }
});

function showMsg(txt, type){
  modalMsg.textContent = txt;
  modalMsg.className = "msg " + (type || "");
}

function closeModal(){
  modal.classList.add("hidden");
  modal.setAttribute("aria-hidden", "true");
}

loadAll();
