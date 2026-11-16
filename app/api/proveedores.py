from __future__ import annotations 
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base import get_session
from app.repositories.proveedor_repo import ProveedorRepository
from typing import List
router = APIRouter(prefix="/api/proveedores", tags=["proveedores"])


class ProveedorIn(BaseModel):
    nombre: str
    telefono: str | None = None
    direccion: str | None = None
    nota: str | None = None


class ProveedorOut(BaseModel):
    id: int
    nombre: str
    telefono: str | None
    direccion: str | None
    nota: str | None

    class Config:
        from_attributes = True


def _repo(session: Session = Depends(get_session)) -> ProveedorRepository:
    return ProveedorRepository(session)


@router.get("/", response_model=List[ProveedorOut])
def listar(repo: ProveedorRepository = Depends(_repo)):
    return repo.listar()


@router.post("/", response_model=ProveedorOut, status_code=201)
def crear(data: ProveedorIn, repo: ProveedorRepository = Depends(_repo)):
    if not data.nombre:
        raise HTTPException(status_code=400, detail="Nombre obligatorio")
    return repo.crear(**data.model_dump())
