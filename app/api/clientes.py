from __future__ import annotations 
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from app.db.base import get_session
from app.repositories.cliente_repo import ClienteRepository

router = APIRouter(prefix="/api/clientes", tags=["clientes"])


class ClienteIn(BaseModel):
    nombre: str
    telefono: str | None = None
    direccion: str | None = None
    nota: str | None = None


class ClienteOut(BaseModel):
    id: int
    nombre: str
    telefono: str | None
    direccion: str | None
    nota: str | None

    class Config:
        from_attributes = True


def _repo(session: Session = Depends(get_session)) -> ClienteRepository:
    return ClienteRepository(session)


@router.get("/", response_model=List[ClienteOut])
def listar(repo: ClienteRepository = Depends(_repo)):
    return repo.listar()


@router.post("/", response_model=ClienteOut, status_code=201)
def crear(data: ClienteIn, repo: ClienteRepository = Depends(_repo)):
    if not data.nombre:
        raise HTTPException(status_code=400, detail="Nombre obligatorio")
    return repo.crear(**data.model_dump())
