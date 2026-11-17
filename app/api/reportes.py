from __future__ import annotations
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_session
from app.repositories.reporte_repo import ReporteRepository
from app.services.reporte_service import ReporteService

router = APIRouter(prefix="/api/reportes", tags=["reportes"])


def _service(session: Session = Depends(get_session)) -> ReporteService:
    return ReporteService(ReporteRepository(session))


@router.get("/ventas-dia")
def ventas_dia(fecha: str | None = None,
               service: ReporteService = Depends(_service)):
    try:
        f = date.fromisoformat(fecha) if fecha else date.today()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido (YYYY-MM-DD)")
    return service.ventas_dia(f)