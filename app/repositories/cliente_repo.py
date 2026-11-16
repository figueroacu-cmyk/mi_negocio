from __future__ import annotations 
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Cliente


class ClienteRepository:
    def __init__(self, session: Session):
        self.session = session

    def crear(self, nombre: str, telefono: str | None = None,
              direccion: str | None = None, nota: str | None = None) -> Cliente:
        c = Cliente(nombre=nombre, telefono=telefono, direccion=direccion, nota=nota)
        self.session.add(c)
        self.session.commit()
        self.session.refresh(c)
        return c

    def listar(self) -> list[Cliente]:
        stmt = select(Cliente).where(Cliente.activo == True).order_by(Cliente.nombre)  # noqa
        return list(self.session.execute(stmt).scalars())

    def obtener(self, cliente_id: int) -> Cliente | None:
        return self.session.get(Cliente, cliente_id)