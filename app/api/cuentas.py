from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base import get_session
from app.repositories.cliente_repo import ClienteRepository
from app.repositories.venta_repo import VentaRepository

router = APIRouter(prefix="/api/cuentas", tags=["cuentas"])


class VentaPendienteOut(BaseModel):
    id: int
    fecha: str
    total: float
    total_abonado: float
    saldo: float
    tipo_pago: str

    class Config:
        from_attributes = True


@router.get("/{cliente_id}")
def deuda_cliente(cliente_id: int, session: Session = Depends(get_session)):
    cliente = ClienteRepository(session).obtener(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    ventas = VentaRepository(session).listar_pendientes_por_cliente(cliente_id)
    pendientes = [
        {
            "id": v.id,
            "fecha": v.fecha.isoformat() if v.fecha else None,
            "total": float(v.total),
            "total_abonado": v.total_abonado,
            "saldo": v.saldo,
            "tipo_pago": v.tipo_pago,
        }
        for v in ventas
    ]
    deuda_total = sum(p["saldo"] for p in pendientes)
    return {
        "cliente": {"id": cliente.id, "nombre": cliente.nombre},
        "deuda_total": deuda_total,
        "ventas_pendientes": pendientes,
    }