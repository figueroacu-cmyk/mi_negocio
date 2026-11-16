from __future__ import annotations 
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base import get_session
from app.repositories.compra_repo import CompraRepository
from app.repositories.producto_repo import ProductoRepository
from app.repositories.proveedor_repo import ProveedorRepository
from app.services.compra_service import CompraService
from datetime import datetime
from typing import List
router = APIRouter(prefix="/api/compras", tags=["compras"])


class LineaIn(BaseModel):
    producto_id: int | None = None
    producto_nombre: str | None = None
    precio_venta: float | None = None
    cantidad: int
    precio_compra: float


class CompraIn(BaseModel):
    proveedor_id: int | None = None
    numero_factura: str | None = None
    nota: str | None = None
    fecha: datetime | None = None
    tasa_cambio: float = 0
    lineas: list[LineaIn]
    
class CompraOut(BaseModel):
    id: int
    proveedor_id: int | None
    numero_factura: str | None
    nota: str | None
    total: float
    fecha: datetime
    
    class Config:
        from_attributes = True


def _service(session: Session = Depends(get_session)) -> CompraService:
    return CompraService(
        CompraRepository(session),
        ProductoRepository(session),
        ProveedorRepository(session),
    )


@router.get("/", response_model=List[CompraOut])
def listar(service: CompraService = Depends(_service)):
    return service.listar()


@router.post("/", response_model=CompraOut, status_code=201)
def registrar(data: CompraIn, service: CompraService = Depends(_service)):
    try:
        return service.registrar(
            proveedor_id=data.proveedor_id,
            numero_factura=data.numero_factura,
            nota=data.nota,
            fecha=data.fecha,
            tasa_cambio=data.tasa_cambio,
            lineas=[ln.model_dump() for ln in data.lineas],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
