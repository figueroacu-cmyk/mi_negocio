from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base import get_session
from app.repositories.configuracion_repo import ConfiguracionRepository
from app.services.configuracion_service import ConfiguracionService

router = APIRouter(prefix="/api/configuracion", tags=["configuracion"])


class ConfiguracionOut(BaseModel):
    tasa_cambio: float
    fecha_actualizacion: str | None

    class Config:
        from_attributes = True


class TasaIn(BaseModel):
    tasa_cambio: float


def _service(session: Session = Depends(get_session)) -> ConfiguracionService:
    return ConfiguracionService(ConfiguracionRepository(session))


@router.get("/", response_model=ConfiguracionOut)
def obtener(service: ConfiguracionService = Depends(_service)):
    config = service.obtener()
    return ConfiguracionOut(
        tasa_cambio=float(config.tasa_cambio),
        fecha_actualizacion=config.fecha_actualizacion.isoformat() if config.fecha_actualizacion else None,
    )


@router.put("/", response_model=ConfiguracionOut)
def actualizar(data: TasaIn, service: ConfiguracionService = Depends(_service)):
    try:
        config = service.actualizar_tasa(data.tasa_cambio)
        return ConfiguracionOut(
            tasa_cambio=float(config.tasa_cambio),
            fecha_actualizacion=config.fecha_actualizacion.isoformat() if config.fecha_actualizacion else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))