from __future__ import annotations 
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base import get_session
from app.repositories.producto_repo import ProductoRepository
from app.services.producto_service import ProductoService
from app.services.imagen_service import ImagenService
from typing import List
router = APIRouter(prefix="/api/productos", tags=["productos"])


class ProductoIn(BaseModel):
    nombre: str
    precio_costo: float
    precio_dueno: float
    precio_vendedor: float
    stock: int = 0
    stock_minimo: int = 5
    descripcion: str | None = None
    categoria: str | None = None
    imagen: str | None = None

class ProductoUpdate(BaseModel):
    nombre: str | None = None
    precio_costo: float | None = None
    precio_dueno: float | None = None
    precio_vendedor: float | None = None
    precio_cliente: float | None = None
    stock: int | None = None
    stock_minimo: int | None = None
    descripcion: str | None = None
    categoria: str | None = None
    imagen: str | None = None


class ProductoOut(BaseModel):
    id: int
    nombre: str
    precio_costo: float
    precio_dueno: float
    precio_vendedor: float
    precio_cliente: float
    stock: int
    stock_minimo: int
    descripcion: str | None
    categoria: str | None
    imagen: str | None

    class Config:
        from_attributes = True

        
def _service(session: Session = Depends(get_session)) -> ProductoService:
    return ProductoService(ProductoRepository(session))


@router.get("/", response_model=List[ProductoOut])
def listar(service: ProductoService = Depends(_service)):
    return service.listar()


@router.get("/{producto_id}", response_model=ProductoOut)
def obtener(producto_id: int, service: ProductoService = Depends(_service)):
    try:
        return service.obtener(producto_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=ProductoOut, status_code=201)
def crear(data: ProductoIn, service: ProductoService = Depends(_service)):
    try:
        return service.crear(**data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{producto_id}", response_model=ProductoOut)
def actualizar(producto_id: int, data: ProductoUpdate,
               service: ProductoService = Depends(_service)):
    try:
        campos = data.model_dump(exclude_unset=True)
        return service.actualizar(producto_id, **campos)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{producto_id}", status_code=204)
def desactivar(producto_id: int, service: ProductoService = Depends(_service)):
    try:
        service.desactivar(producto_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{producto_id}/imagen", response_model=ProductoOut)
def subir_imagen(producto_id: int, archivo: UploadFile = File(...),
                 service: ProductoService = Depends(_service)):
    try:
        producto = service.obtener(producto_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    imagen_service = ImagenService()

    # Borrar la imagen anterior si existía
    if producto.imagen:
        imagen_service.eliminar(producto.imagen)

    try:
        nombre = imagen_service.guardar(archivo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return service.actualizar(producto_id, imagen=nombre)


@router.delete("/{producto_id}/imagen", response_model=ProductoOut)
def eliminar_imagen(producto_id: int, service: ProductoService = Depends(_service)):
    try:
        producto = service.obtener(producto_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if producto.imagen:
        ImagenService().eliminar(producto.imagen)
        service.actualizar(producto_id, imagen=None)
    return service.obtener(producto_id)
