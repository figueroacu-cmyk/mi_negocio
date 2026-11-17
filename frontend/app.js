// ==================== UTILIDADES ====================

const API_PRODUCTOS = "/api/productos";
const API_PROVEEDORES = "/api/proveedores";
const API_COMPRAS = "/api/compras";
const API_CLIENTES = "/api/clientes";
const API_VENTAS = "/api/ventas";
const API_CUENTAS = "/api/cuentas";
const API_CONFIGURACION = "/api/configuracion";
const API_REPORTES = "/api/reportes";

let editandoProductoId = null;
let productosCache = [];
let proveedoresCache = [];
let clientesCache = [];

function formatearFecha(iso) {
  if (!iso) return "-";
  const limpio = iso.replace(" ", "T").split(".")[0];
  const d = new Date(limpio);
  if (isNaN(d.getTime())) return iso;
  const pad = (n) => String(n).padStart(2, "0");
  return `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function ponerFechaHoy(inputId) {
  const input = document.querySelector(inputId);
  if (!input) return;
  const hoy = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  input.value = `${hoy.getFullYear()}-${pad(hoy.getMonth() + 1)}-${pad(hoy.getDate())}`;
}

// ==================== PESTAÑAS ====================

document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById("tab-" + btn.dataset.tab).classList.add("active");

    // Refrescar datos al cambiar de pestaña
    if (btn.dataset.tab === "cuentas") cargarCuentas();
  });
});

// ==================== PRODUCTOS ====================

async function cargarProductos() {
  const res = await fetch(API_PRODUCTOS + "/");
  productosCache = await res.json();
  const tbody = document.querySelector("#tabla-productos tbody");
  tbody.innerHTML = "";
  for (const p of productosCache) {
    const tr = document.createElement("tr");
    const miniatura = p.imagen
      ? `<img src="/uploads/productos/${p.imagen}" alt="${p.nombre}" style="max-width:60px;max-height:60px;">`
      : "-";
    tr.innerHTML = `
      <td>${p.id}</td>
      <td>${p.nombre}</td>
	  <td>${p.precio_costo}</td>
      <td>${p.precio_dueno}</td>
	  <td>${p.precio_vendedor}</td>
	  <td>${p.precio_cliente}</td>
      <td>${p.stock}</td>
      <td>${p.categoria ?? "-"}</td>
      <td>
        <button data-accion="editar" data-id="${p.id}">Editar</button>
        <button data-accion="eliminar" data-id="${p.id}">Eliminar</button>
      </td>
    `;
    tbody.appendChild(tr);
  }
}

async function cargarProductoEnFormulario(id) {
  const res = await fetch(`${API_PRODUCTOS}/${id}`);
  if (!res.ok) return alert("No se pudo cargar el producto");
  const p = await res.json();
  const form = document.querySelector("#form-producto");
  form.nombre.value = p.nombre;
  form.precio_costo.value = p.precio_costo;
  form.precio_dueno.value = p.precio_dueno;
  form.precio_vendedor.value = p.precio_vendedor;
  form.precio_cliente.value = p.precio_cliente;
  form.stock.value = p.stock;
  form.stock_minimo.value = p.stock_minimo;
  form.categoria.value = p.categoria ?? "";
  form.descripcion.value = p.descripcion ?? "";
  editandoProductoId = id;
  document.querySelector("#btn-guardar-producto").textContent = "Actualizar";
  document.querySelector("#btn-cancelar-producto").style.display = "inline";
}

function resetFormularioProducto() {
  document.querySelector("#form-producto").reset();
  editandoProductoId = null;
  document.querySelector("#btn-guardar-producto").textContent = "Agregar";
  document.querySelector("#btn-cancelar-producto").style.display = "none";
}

document.querySelector("#form-producto").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  const data = {
    nombre: form.nombre.value,
    precio_costo: parseFloat(form.precio_costo.value),
    precio_dueno: parseFloat(form.precio_dueno.value),
    precio_vendedor: parseFloat(form.precio_vendedor.value),
    precio_cliente: parseFloat(form.precio_cliente.value),
    stock: parseInt(form.stock.value) || 0,
    stock_minimo: parseInt(form.stock_minimo.value) || 5,
    categoria: form.categoria.value || null,
    descripcion: form.descripcion.value || null,
    imagen: form.imagen?.value || null,
  };
  const url = editandoProductoId ? `${API_PRODUCTOS}/${editandoProductoId}` : API_PRODUCTOS + "/";
  const method = editandoProductoId ? "PUT" : "POST";

  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    const err = await res.json();
    return alert("Error: " + (err.detail || "desconocido"));
  }

  const producto = await res.json();

  const archivo = form.imagen.files[0];
  if (archivo) {
    const fd = new FormData();
    fd.append("archivo", archivo);
    const resImg = await fetch(`${API_PRODUCTOS}/${producto.id}/imagen`, {
      method: "POST",
      body: fd,
    });
    if (!resImg.ok) {
      const err = await resImg.json();
      alert("Producto guardado, pero falló la imagen: " + (err.detail || "desconocido"));
    }
  }

  resetFormularioProducto();
  cargarProductos();
});

document.querySelector("#btn-cancelar-producto").addEventListener("click", resetFormularioProducto);

document.querySelector("#tabla-productos").addEventListener("click", async (e) => {
  const btn = e.target.closest("button");
  if (!btn) return;
  const id = parseInt(btn.dataset.id);
  if (btn.dataset.accion === "editar") {
    cargarProductoEnFormulario(id);
  } else if (btn.dataset.accion === "eliminar") {
    if (!confirm("¿Desactivar este producto?")) return;
    const res = await fetch(`${API_PRODUCTOS}/${id}`, { method: "DELETE" });
    if (res.ok) cargarProductos();
    else alert("No se pudo desactivar");
  }
});

// Cálculo automático sugerido: dueño + vendedor = cliente (editable)
const formProducto = document.querySelector("#form-producto");
["precio_dueno", "precio_vendedor"].forEach((name) => {
  formProducto[name].addEventListener("input", () => {
    const dueno = parseFloat(formProducto.precio_dueno.value) || 0;
    const vendedor = parseFloat(formProducto.precio_vendedor.value) || 0;
    formProducto.precio_cliente.value = (dueno + vendedor).toFixed(2);
  });
});

// ==================== PROVEEDORES ====================

async function cargarProveedores() {
  const res = await fetch(API_PROVEEDORES + "/");
  proveedoresCache = await res.json();
  const tbody = document.querySelector("#tabla-proveedores tbody");
  tbody.innerHTML = "";
  for (const p of proveedoresCache) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${p.id}</td><td>${p.nombre}</td>
      <td>${p.telefono ?? "-"}</td><td>${p.direccion ?? "-"}</td><td>${p.nota ?? "-"}</td>
    `;
    tbody.appendChild(tr);
  }
  const select = document.querySelector("#select-proveedor");
  if (select) {
    select.innerHTML = '<option value="">Sin proveedor</option>';
    for (const p of proveedoresCache) {
      const opt = document.createElement("option");
      opt.value = p.id;
      opt.textContent = p.nombre;
      select.appendChild(opt);
    }
  }
}

document.querySelector("#form-proveedor").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  const data = {
    nombre: form.nombre.value,
    telefono: form.telefono.value || null,
    direccion: form.direccion.value || null,
    nota: form.nota.value || null,
  };
  const res = await fetch(API_PROVEEDORES + "/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (res.ok) {
    form.reset();
    cargarProveedores();
  } else {
    const err = await res.json();
    alert("Error: " + (err.detail || "desconocido"));
  }
});

// ==================== COMPRAS ====================

function opcionesProductos(seleccionadoId = "") {
  let html = '<option value="">-- Producto nuevo --</option>';
  for (const p of productosCache) {
    const sel = p.id === seleccionadoId ? "selected" : "";
    html += `<option value="${p.id}" ${sel}>${p.nombre} (stock ${p.stock})</option>`;
  }
  return html;
}

function opcionesProductosVenta(seleccionadoId = "") {
  let html = '<option value="">-- Elegir producto --</option>';
  for (const p of productosCache) {
    const sel = p.id === seleccionadoId ? "selected" : "";
    html += `<option value="${p.id}" data-precio="${p.precio_cliente}" ${sel}>${p.nombre} (stock ${p.stock})</option>`;
  }
  return html;
}

function agregarLinea() {
  const tbody = document.querySelector("#tabla-lineas tbody");
  const tr = document.createElement("tr");
  tr.innerHTML = `
    <td>
      <select class="linea-producto">${opcionesProductos()}</select>
      <input class="linea-nombre-nuevo" placeholder="Nombre nuevo" style="display:none;">
      <input class="linea-precio-venta" type="number" step="0.01" placeholder="Precio venta" style="display:none;">
    </td>
    <td><input class="linea-cantidad" type="number" value="1" min="1"></td>
    <td><input class="linea-precio-compra" type="number" step="0.01" value="0"></td>
    <td class="linea-subtotal">0.00</td>
    <td><button type="button" class="btn-quitar-linea">X</button></td>
  `;
  tbody.appendChild(tr);
  conectarEventosLinea(tr);
}

function conectarEventosLinea(tr) {
  const select = tr.querySelector(".linea-producto");
  const nombreNuevo = tr.querySelector(".linea-nombre-nuevo");
  const precioVenta = tr.querySelector(".linea-precio-venta");

  function actualizarVisibilidad() {
    const esNuevo = select.value === "";
    nombreNuevo.style.display = esNuevo ? "inline-block" : "none";
    precioVenta.style.display = esNuevo ? "inline-block" : "none";
    recalcularTotal();
  }

  select.addEventListener("change", actualizarVisibilidad);
  select.addEventListener("input", actualizarVisibilidad);

  tr.querySelectorAll("input").forEach(el => {
    el.addEventListener("input", recalcularTotal);
  });

  tr.querySelector(".btn-quitar-linea").addEventListener("click", () => {
    tr.remove();
    recalcularTotal();
  });

  actualizarVisibilidad();
}

function recalcularTotal() {
  let total = 0;
  document.querySelectorAll("#tabla-lineas tbody tr").forEach(tr => {
    const cant = parseInt(tr.querySelector(".linea-cantidad").value) || 0;
    const precio = parseFloat(tr.querySelector(".linea-precio-compra").value) || 0;
    const sub = cant * precio;
    tr.querySelector(".linea-subtotal").textContent = sub.toFixed(2);
    total += sub;
  });
  document.querySelector("#total-compra").textContent = total.toFixed(2);
}

document.querySelector("#btn-agregar-linea").addEventListener("click", agregarLinea);

document.querySelector("#form-compra").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  const lineas = [];
  document.querySelectorAll("#tabla-lineas tbody tr").forEach(tr => {
    const productoId = tr.querySelector(".linea-producto").value;
    const nombreNuevo = tr.querySelector(".linea-nombre-nuevo").value;
    const precioVenta = parseFloat(tr.querySelector(".linea-precio-venta").value) || null;
    const cantidad = parseInt(tr.querySelector(".linea-cantidad").value) || 0;
    const precioCompra = parseFloat(tr.querySelector(".linea-precio-compra").value) || 0;

    if (!productoId && !nombreNuevo) return;
    if (cantidad <= 0) return;

    lineas.push({
      producto_id: productoId ? parseInt(productoId) : null,
      producto_nombre: productoId ? null : nombreNuevo,
      precio_venta: productoId ? null : precioVenta,
      cantidad: cantidad,
      precio_compra: precioCompra,
    });
  });

  if (lineas.length === 0) return alert("Añade al menos una línea válida");

  const data = {
    proveedor_id: form.proveedor_id.value ? parseInt(form.proveedor_id.value) : null,
    numero_factura: form.numero_factura.value || null,
    nota: form.nota.value || null,
    fecha: form.fecha.value ? form.fecha.value + "T00:00:00" : null,
    lineas: lineas,
  };

  const res = await fetch(API_COMPRAS + "/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (res.ok) {
    form.reset();
    ponerFechaHoy("#input-fecha-compra");
    document.querySelector("#tabla-lineas tbody").innerHTML = "";
    document.querySelector("#total-compra").textContent = "0.00";
    await cargarProductos();
    await cargarCompras();
    alert("Compra registrada");
  } else {
    const err = await res.json();
    alert("Error: " + (err.detail || "desconocido"));
  }
});

async function cargarCompras() {
  const res = await fetch(API_COMPRAS + "/");
  const compras = await res.json();
  const tbody = document.querySelector("#tabla-compras tbody");
  tbody.innerHTML = "";
  for (const c of compras) {
    const prov = proveedoresCache.find(p => p.id === c.proveedor_id);
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${c.id}</td>
      <td>${prov ? prov.nombre : "Sin proveedor"}</td>
      <td>${c.numero_factura ?? "-"}</td>
      <td>${c.total}</td>
      <td>${formatearFecha(c.fecha)}</td>
    `;
    tbody.appendChild(tr);
  }
}

// ==================== CLIENTES ====================

async function cargarClientes() {
  const res = await fetch(API_CLIENTES + "/");
  clientesCache = await res.json();
  const tbody = document.querySelector("#tabla-clientes tbody");
  tbody.innerHTML = "";
  for (const c of clientesCache) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${c.id}</td><td>${c.nombre}</td>
      <td>${c.telefono ?? "-"}</td><td>${c.direccion ?? "-"}</td><td>${c.nota ?? "-"}</td>
    `;
    tbody.appendChild(tr);
  }
  const select = document.querySelector("#select-cliente");
  if (select) {
    select.innerHTML = '<option value="">Cliente general</option>';
    for (const c of clientesCache) {
      const opt = document.createElement("option");
      opt.value = c.id;
      opt.textContent = c.nombre;
      select.appendChild(opt);
    }
  }
}

document.querySelector("#form-cliente").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  const data = {
    nombre: form.nombre.value,
    telefono: form.telefono.value || null,
    direccion: form.direccion.value || null,
    nota: form.nota.value || null,
  };
  const res = await fetch(API_CLIENTES + "/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (res.ok) {
    form.reset();
    cargarClientes();
  } else {
    const err = await res.json();
    alert("Error: " + (err.detail || "desconocido"));
  }
});

// ==================== VENTAS ====================

function agregarLineaVenta() {
  const tbody = document.querySelector("#tabla-lineas-venta tbody");
  const tr = document.createElement("tr");
  tr.innerHTML = `
    <td>
      <select class="linea-producto-venta">${opcionesProductosVenta()}</select>
    </td>
    <td><input class="linea-cantidad-venta" type="number" value="1" min="1"></td>
    <td><input class="linea-precio-venta-venta" type="number" step="0.01" value="0"></td>
    <td class="linea-subtotal-venta">0.00</td>
    <td><button type="button" class="btn-quitar-linea-venta">X</button></td>
  `;
  tbody.appendChild(tr);
  conectarEventosLineaVenta(tr);
}

function conectarEventosLineaVenta(tr) {
  const select = tr.querySelector(".linea-producto-venta");
  const precioInput = tr.querySelector(".linea-precio-venta-venta");

  function alCambiarProducto() {
    const opt = select.selectedOptions[0];
    const precio = parseFloat(opt?.dataset?.precio);
    if (!isNaN(precio)) precioInput.value = precio;
    recalcularTotalVenta();
  }

  select.addEventListener("change", alCambiarProducto);

  tr.querySelectorAll("input").forEach(el => {
    el.addEventListener("input", recalcularTotalVenta);
  });

  tr.querySelector(".btn-quitar-linea-venta").addEventListener("click", () => {
    tr.remove();
    recalcularTotalVenta();
  });
}

function recalcularTotalVenta() {
  let total = 0;
  document.querySelectorAll("#tabla-lineas-venta tbody tr").forEach(tr => {
    const cant = parseInt(tr.querySelector(".linea-cantidad-venta").value) || 0;
    const precio = parseFloat(tr.querySelector(".linea-precio-venta-venta").value) || 0;
    const sub = cant * precio;
    tr.querySelector(".linea-subtotal-venta").textContent = sub.toFixed(2);
    total += sub;
  });
  document.querySelector("#total-venta").textContent = total.toFixed(2);
}

document.querySelector("#btn-agregar-linea-venta").addEventListener("click", agregarLineaVenta);

document.querySelector("#select-tipo-pago").addEventListener("change", (e) => {
  const bloque = document.querySelector("#bloque-credito");
  bloque.style.display = e.target.value === "credito" ? "block" : "none";
});

// ===== FLUJO DE CAJA REGISTRADORA =====
let ventaPendiente = null; // guarda la venta recién registrada mientras se cobra

function abrirModalCobro(venta, tasa) {
  ventaPendiente = venta;
  const totalUsd = parseFloat(venta.total) || 0;
  const totalCup = parseFloat(venta.total_cup) || (totalUsd * tasa);

  document.querySelector("#cobro-total-usd").textContent = "$" + totalUsd.toFixed(2);
  document.querySelector("#cobro-tasa").textContent = tasa.toFixed(2);
  document.querySelector("#cobro-total-cup").textContent = "$" + totalCup.toFixed(2);
  document.querySelector("#cobro-moneda").value = "CUP";
  document.querySelector("#cobro-importe").value = "";
  document.querySelector("#cobro-vuelto").textContent = "$0.00";
  document.querySelector("#cobro-vuelto").style.color = "#0a7d0a";
  document.querySelector("#cobro-error").style.display = "none";
  document.querySelector("#modal-cobro").style.display = "flex";
  document.querySelector("#cobro-importe").focus();

  recalcularVuelto();
}

function recalcularVuelto() {
  if (!ventaPendiente) return;
  const totalUsd = parseFloat(ventaPendiente.total) || 0;
  const tasa = parseFloat(document.querySelector("#cobro-tasa").textContent) || 0;
  const totalCup = totalUsd * tasa;
  const moneda = document.querySelector("#cobro-moneda").value;
  const importe = parseFloat(document.querySelector("#cobro-importe").value) || 0;

  let vueltoCup;
  if (moneda === "CUP") {
    vueltoCup = importe - totalCup;
  } else {
    // Pagó en USD: convertir a CUP
    vueltoCup = (importe * tasa) - totalCup;
  }

  const el = document.querySelector("#cobro-vuelto");
  const err = document.querySelector("#cobro-error");

  if (importe === 0) {
    el.textContent = "$0.00";
    el.style.color = "#0a7d0a";
    err.style.display = "none";
  } else if (vueltoCup < 0) {
    el.textContent = "$" + vueltoCup.toFixed(2);
    el.style.color = "#c00";
    err.textContent = "El importe es menor al total. Por ahora no se permite venta a crédito desde aquí.";
    err.style.display = "block";
  } else {
    el.textContent = "$" + vueltoCup.toFixed(2);
    el.style.color = "#0a7d0a";
    err.style.display = "none";
  }
}

function cerrarModalCobro() {
  document.querySelector("#modal-cobro").style.display = "none";
  ventaPendiente = null;
}

document.querySelector("#cobro-moneda").addEventListener("change", recalcularVuelto);
document.querySelector("#cobro-importe").addEventListener("input", recalcularVuelto);
document.querySelector("#cobro-cancelar").addEventListener("click", () => {
  // La venta ya está registrada en BD. Solo cerramos el modal.
  cerrarModalCobro();
  // Refrescar productos y ventas
  cargarProductos();
  cargarVentas();
});
document.querySelector("#cobro-confirmar").addEventListener("click", () => {
  const importe = parseFloat(document.querySelector("#cobro-importe").value) || 0;
  if (importe <= 0) {
    alert("Ingresa el importe recibido");
    return;
  }
  const totalUsd = parseFloat(ventaPendiente.total) || 0;
  const tasa = parseFloat(document.querySelector("#cobro-tasa").textContent) || 0;
  const totalCup = totalUsd * tasa;
  const moneda = document.querySelector("#cobro-moneda").value;
  const vueltoCup = (moneda === "CUP" ? importe : importe * tasa) - totalCup;

  if (vueltoCup < 0) {
    alert("El importe es menor al total. No se puede confirmar el cobro.");
    return;
  }

  alert("Venta cobrada. Vuelto: $" + vueltoCup.toFixed(2) + " CUP");
  cerrarModalCobro();
  cargarProductos();
  cargarVentas();
});

// ===== SUBMIT DE VENTA =====
document.querySelector("#form-venta").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;

  const lineas = [];
  document.querySelectorAll("#tabla-lineas-venta tbody tr").forEach(tr => {
    const productoId = tr.querySelector(".linea-producto-venta").value;
    const cantidad = parseInt(tr.querySelector(".linea-cantidad-venta").value) || 0;

    if (!productoId || cantidad <= 0) return;

    const producto = productosCache.find(p => p.id === parseInt(productoId));
    if (!producto) return;

    lineas.push({
      producto_id: parseInt(productoId),
      cantidad: parseInt(cantidad),
      precio_dueno: producto.precio_dueno,
      precio_vendedor: producto.precio_vendedor,
      precio_cliente: producto.precio_cliente,
    });
  });

  if (lineas.length === 0) return alert("Añade al menos una línea válida");

  const tipoPago = form.tipo_pago.value;
  const data = {
    cliente_id: form.cliente_id.value ? parseInt(form.cliente_id.value) : null,
    fecha: form.fecha.value ? form.fecha.value + "T00:00:00" : null,
    nota: form.nota.value || null,
    tipo_pago: tipoPago,
    lineas: lineas,
    abono_inicial: tipoPago === "credito" ? (parseFloat(form.abono_inicial.value) || 0) : 0,
    tipo_pago_abono: tipoPago === "credito" ? form.tipo_pago_abono.value : null,
  };

  const res = await fetch(API_VENTAS + "/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (res.ok) {
    const venta = await res.json();

    // Limpiar el formulario
    form.reset();
    ponerFechaHoy("#input-fecha-venta");
    document.querySelector("#bloque-credito").style.display = "none";
    document.querySelector("#tabla-lineas-venta tbody").innerHTML = "";
    document.querySelector("#total-venta").textContent = "0.00";

    // Obtener la tasa vigente y abrir el modal de cobro
    try {
      const resTasa = await fetch(API_CONFIGURACION + "/");
      if (!resTasa.ok) throw new Error("No se pudo obtener la tasa");
      const config = await resTasa.json();
      abrirModalCobro(venta, parseFloat(config.tasa_cambio));
    } catch (err) {
      // Si falla la tasa, mostramos el ticket con la tasa que trajo la venta
      abrirModalCobro(venta, parseFloat(venta.tasa_cambio) || 0);
    }
  } else {
    const err = await res.json();
    alert("Error: " + (err.detail || "desconocido"));
  }
});

async function cargarVentas() {
  const res = await fetch(API_VENTAS + "/");
  const ventas = await res.json();
  const tbody = document.querySelector("#tabla-ventas tbody");
  tbody.innerHTML = "";
  for (const v of ventas) {
    const cli = clientesCache.find(c => c.id === v.cliente_id);
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${v.id}</td>
      <td>${formatearFecha(v.fecha)}</td>
      <td>${cli ? cli.nombre : "Cliente general"}</td>
      <td>${v.tipo_pago}</td>
      <td>${v.estado}</td>
      <td>${v.total}</td>
      <td>${v.total_abonado}</td>
      <td>${v.saldo}</td>
    `;
    tbody.appendChild(tr);
  }
}

// ==================== CUENTAS ====================

async function cargarCuentas() {
  const tbody = document.querySelector("#tabla-cuentas tbody");
  tbody.innerHTML = "";

  // Cargar deuda de cada cliente en paralelo
  const resultados = await Promise.all(
    clientesCache.map(async (c) => {
      const res = await fetch(`${API_CUENTAS}/${c.id}`);
      const data = await res.json();
      return { cliente: c, deuda: data.deuda_total };
    })
  );

  for (const r of resultados) {
    if (r.deuda <= 0.001) continue;
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${r.cliente.nombre}</td>
      <td>${r.deuda.toFixed(2)}</td>
      <td><button data-accion="detalle" data-id="${r.cliente.id}">Ver detalle</button></td>
    `;
    tbody.appendChild(tr);
  }
}

document.querySelector("#tabla-cuentas").addEventListener("click", async (e) => {
  const btn = e.target.closest("button");
  if (!btn) return;
  const clienteId = parseInt(btn.dataset.id);
  await cargarDetalleCuenta(clienteId);
});

async function cargarDetalleCuenta(clienteId) {
  const res = await fetch(`${API_CUENTAS}/${clienteId}`);
  const data = await res.json();

  document.querySelector("#detalle-cuenta").style.display = "block";
  document.querySelector("#titulo-detalle-cuenta").textContent =
    `Deudas de ${data.cliente.nombre} — Total: ${data.deuda_total.toFixed(2)}`;

  const tbody = document.querySelector("#tabla-detalle-ventas tbody");
  tbody.innerHTML = "";
  for (const v of data.ventas_pendientes) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${v.id}</td>
      <td>${formatearFecha(v.fecha)}</td>
      <td>${v.total}</td>
      <td>${v.total_abonado}</td>
      <td>${v.saldo}</td>
      <td><button data-accion="abonar" data-id="${v.id}" data-saldo="${v.saldo}">Abonar</button></td>
    `;
    tbody.appendChild(tr);
  }
}

document.querySelector("#tabla-detalle-ventas").addEventListener("click", async (e) => {
  const btn = e.target.closest("button");
  if (!btn) return;
  const ventaId = parseInt(btn.dataset.id);
  const saldo = parseFloat(btn.dataset.saldo);

  const monto = prompt(`Saldo pendiente: ${saldo}. ¿Cuánto abona?`, saldo.toString());
  if (!monto) return;
  const montoNum = parseFloat(monto);
  if (isNaN(montoNum) || montoNum <= 0) return alert("Monto inválido");

  const tipo = prompt("Tipo de pago: efectivo / transferencia", "efectivo");
  if (!tipo || !["efectivo", "transferencia"].includes(tipo.toLowerCase())) {
    return alert("Tipo inválido");
  }

  const res = await fetch(`${API_VENTAS}/${ventaId}/abonos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ monto: montoNum, tipo_pago: tipo.toLowerCase(), nota: null }),
  });

  if (res.ok) {
    // Recargar detalle del mismo cliente
    const tr = btn.closest("tr");
    const clienteId = tr.dataset.cliente;
    // Simplemente recargamos desde el detalle actual
    await cargarCuentas();
    document.querySelector("#detalle-cuenta").style.display = "none";
    alert("Abono registrado");
  } else {
    const err = await res.json();
    alert("Error: " + (err.detail || "desconocido"));
  }
});

// ==================== ARRANQUE ====================

(async function init() {
  ponerFechaHoy("#input-fecha-compra");
  ponerFechaHoy("#input-fecha-venta");
  ponerFechaHoy("#input-fecha-cierre");   // ← NUEVA
  await cargarConfiguracion();   // ← esta línea
  await cargarProductos();
  await cargarProveedores();
  await cargarClientes();
  await cargarCompras();
  await cargarVentas();
})();

// ==================== CONFIGURACIÓN ====================

async function cargarConfiguracion() {
  const res = await fetch(API_CONFIGURACION + "/");
  const data = await res.json();
  const form = document.querySelector("#form-configuracion");
  form.tasa_cambio.value = data.tasa_cambio;
  document.querySelector("#fecha-tasa").textContent = data.fecha_actualizacion
    ? `Última actualización: ${formatearFecha(data.fecha_actualizacion)}`
    : "";
}

document.querySelector("#form-configuracion").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  const data = { tasa_cambio: parseFloat(form.tasa_cambio.value) };
  const res = await fetch(API_CONFIGURACION + "/", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (res.ok) {
    alert("Tasa actualizada");
    await cargarConfiguracion();
  } else {
    const err = await res.json();
    alert("Error: " + (err.detail || "desconocido"));
  }
});
  
// ==================== CIERRE DEL DÍA ====================

document.querySelector("#btn-generar-reporte").addEventListener("click", cargarReporteDia);

async function cargarReporteDia() {
  const fechaInput = document.querySelector("#input-fecha-cierre");
  const fecha = fechaInput.value;
  const url = fecha
    ? `${API_REPORTES}/ventas-dia?fecha=${fecha}`
    : `${API_REPORTES}/ventas-dia`;

  const res = await fetch(url);
  if (!res.ok) {
    const err = await res.json();
    return alert("Error: " + (err.detail || "desconocido"));
  }

  const data = await res.json();

  document.querySelector("#reporte-dia").style.display = "block";
  document.querySelector("#rep-total-ventas").textContent = data.total_ventas;
  document.querySelector("#rep-total-usd").textContent = "$" + data.total_usd.toFixed(2);
  document.querySelector("#rep-total-cup").textContent = "$" + data.total_cup.toFixed(2);
  document.querySelector("#rep-total-efectivo").textContent = "$" + data.total_efectivo_cup.toFixed(2);

  // Desglose por tipo de pago
  const tbodyTipos = document.querySelector("#tabla-reporte-tipos tbody");
  tbodyTipos.innerHTML = "";
  for (const [tipo, info] of Object.entries(data.por_tipo_pago)) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${tipo}</td>
      <td>${info.cantidad}</td>
      <td>$${info.total_usd.toFixed(2)}</td>
      <td>$${info.total_cup.toFixed(2)}</td>
    `;
    tbodyTipos.appendChild(tr);
  }

  // Productos vendidos
  const tbodyProds = document.querySelector("#tabla-reporte-productos tbody");
  tbodyProds.innerHTML = "";
  for (const p of data.productos) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${p.nombre}</td>
      <td>${p.cantidad}</td>
      <td>$${p.total_usd.toFixed(2)}</td>
      <td>$${p.total_cup.toFixed(2)}</td>
    `;
    tbodyProds.appendChild(tr);
  }
}   // ← cierre de la función cargarReporteDia

document.querySelector("#btn-generar-reporte").addEventListener("click", cargarReporteDia);
