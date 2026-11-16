# Mi Negocio

Sistema de gestión para un negocio pequeño. Permite administrar productos, proveedores, compras, clientes, ventas (con abonos a crédito) y cuentas por cobrar, trabajando con doble moneda USD/CUP a través de una tasa de cambio configurable.

## Stack técnico

- Python 3.14
- FastAPI
- Uvicorn
- SQLAlchemy 2.0.51
- SQLite
- Pillow
- Frontend vanilla (HTML + CSS + JS)

## Cómo arrancar

1. pip install -r requirements.txt
2. uvicorn app.main:app --reload
3. Abrir http://localhost:8000

Documentación API: http://localhost:8000/docs

## Estructura

app/ (api, services, repositories, db), frontend/, uploads/, mi_negocio.db, requirements.txt

## Reglas de negocio

- La tasa USD/CUP la define el dueño una vez al día en Configuración.
- Cada venta guarda su tasa histórica y total_cup.
- Cada línea guarda tasa_venta y tasa_compra.
- Productos con 4 precios: costo, dueño, vendedor, cliente.
- Compras aumentan stock, ventas lo disminuyen.
- Ventas a crédito requieren cliente y admiten abonos.

## Pendiente post-MVP

- ClienteService y ProveedorService
- Git
- Tests

## Backup

copiar mi_negocio.db a otro lugar antes de cambios grandes.
