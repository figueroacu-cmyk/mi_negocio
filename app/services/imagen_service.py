import uuid
from pathlib import Path

from PIL import Image
from fastapi import UploadFile

from app.config import UPLOADS_PRODUCTOS

# Tamaño máximo (ancho o alto)
MAX_SIZE = 800
CALIDAD_JPEG = 85


class ImagenService:
    def guardar(self, archivo: UploadFile) -> str:
        """
        Procesa y guarda una imagen. Devuelve el nombre del archivo guardado.
        """
        # Validar tipo
        if not archivo.content_type or not archivo.content_type.startswith("image/"):
            raise ValueError("El archivo debe ser una imagen")

        # Nombre único
        extension = ".jpg"  # siempre guardamos como JPEG optimizado
        nombre = f"{uuid.uuid4().hex}{extension}"
        destino = UPLOADS_PRODUCTOS / nombre

        try:
            img = Image.open(archivo.file)
            img = img.convert("RGB")  # por si es PNG con transparencia
            img.thumbnail((MAX_SIZE, MAX_SIZE), Image.LANCZOS)
            img.save(destino, "JPEG", quality=CALIDAD_JPEG, optimize=True)
        except Exception as e:
            raise ValueError(f"No se pudo procesar la imagen: {e}")

        return nombre

    def eliminar(self, nombre_archivo: str) -> None:
        """Elimina una imagen del disco si existe."""
        if not nombre_archivo:
            return
        ruta = UPLOADS_PRODUCTOS / nombre_archivo
        if ruta.exists():
            ruta.unlink()