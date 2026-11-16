from __future__ import annotations 
from datetime import datetime
from app.repositories.configuracion_repo import ConfiguracionRepository
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base import get_session
from app.repositories.venta_repo import VentaRepository
from app.repositories.producto_repo import ProductoRepository
from app.repositories.cliente_repo import ClienteRepository
from app.services.venta_service import VentaService
from typing import List
router = APIRouter(prefix="/api/ventas", tags=["ventas"])


class LineaVentaIn(BaseModel):
    producto_id: int
    cantidad: int
    precio_dueno: float
    precio_vendedor: float
    precio_cliente: float

class VentaIn(BaseModel):
    cliente_id: int | None = None
    fecha: datetime | None = None
    nota: str | None = None
    tipo_pago: str = "efectivo"
    lineas: List[LineaVentaIn]
    abono_inicial: float = 0
    tipo_pago_abono: str | None = None

class AbonoIn(BaseModel):
    monto: float
    tipo_pago: str = "efectivo"
    nota: str | None = None


class AbonoOut(BaseModel):
    id: int
    venta_id: int
    fecha: datetime
    monto: float
    tipo_pago: str
    nota: str | None

    class Config:
        from_attributes = True


class VentaOut(BaseModel):
    id: int
    cliente_id: int | None
    fecha: datetime
    nota: str | None
    total: float
    tasa_cambio: float
    total_cup: float
    tipo_pago: str
    estado: str
    total_abonado: float
    saldo: float

    class Config:
        from_attributes = True

def _service(session: Session = Depends(get_session)) -> VentaService:
    return VentaService(
        VentaRepository(session),
        ProductoRepository(session),
        ClienteRepository(session),
        ConfiguracionRepository(session),
    )

@router.get("/", response_model=List[VentaOut])
def listar(service: VentaService = Depends(_service)):
    return service.listar()


@router.get("/{venta_id}", response_model=VentaOut)
def obtener(venta_id: int, service: VentaService = Depends(_service)):
    try:
        return service.obtener(venta_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=VentaOut, status_code=201)
def registrar(data: VentaIn, service: VentaService = Depends(_service)):
    try:
        return service.registrar(
            cliente_id=data.cliente_id,
            fecha=data.fecha,
            nota=data.nota,
            tipo_pago=data.tipo_pago,
            lineas=[ln.model_dump() for ln in data.lineas],
            abono_inicial=data.abono_inicial,
            tipo_pago_abono=data.tipo_pago_abono,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{venta_id}/abonos", response_model=List[AbonoOut])
def listar_abonos(venta_id: int, service: VentaService = Depends(_service)):
    try:
        venta = service.obtener(venta_id)
        return venta.abonos
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{venta_id}/abonos", response_model=AbonoOut, status_code=201)
def abonar(venta_id: int, data: AbonoIn, service: VentaService = Depends(_service)):
    try:
        return service.abonar(venta_id, data.monto, data.tipo_pago, data.nota)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
