from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import FRONTEND_DIR, UPLOADS_DIR
from app.db.base import init_db
from app.api import productos, proveedores, compras, clientes, ventas, cuentas, configuracion

app = FastAPI(title="Mi Negocio")

init_db()

app.include_router(productos.router)
app.include_router(proveedores.router)
app.include_router(compras.router)
app.include_router(clientes.router)
app.include_router(ventas.router)
app.include_router(cuentas.router)
app.include_router(configuracion.router)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")


@app.get("/")
def index():
    return FileResponse(FRONTEND_DIR / "index.html")
