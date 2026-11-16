# Mi Negocio

Sistema de gestión para un negocio pequeño. Permite administrar productos,
proveedores, compras, clientes, ventas (con abonos a crédito) y cuentas por
cobrar, trabajando con doble moneda USD/CUP a través de una tasa de cambio
configurable.

---

## Stack técnico

- **Python 3.14**
- **FastAPI** — API REST
- **Uvicorn** — servidor ASGI
- **SQLAlchemy 2.0.51** — ORM
- **SQLite** — base de datos (`mi_negocio.db`)
- **Pillow** — procesamiento de imágenes de productos
- **Frontend vanilla** — HTML + CSS + JavaScript (`frontend/`)

Dependencias en `requirements.txt`:
