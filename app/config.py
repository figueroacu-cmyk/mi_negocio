from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "mi_negocio.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

HOST = "0.0.0.0"
PORT = 8000

FRONTEND_DIR = BASE_DIR / "frontend"
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_PRODUCTOS = UPLOADS_DIR / "productos"

# Crear las carpetas si no existen
UPLOADS_PRODUCTOS.mkdir(parents=True, exist_ok=True)