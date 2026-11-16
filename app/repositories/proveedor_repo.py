from __future__ import annotations 
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Proveedor


class ProveedorRepository:
    def __init__(self, session: Session):
        self.session = session

    def crear(self, nombre: str, telefono: str | None = None,
              direccion: str | None = None, nota: str | None = None) -> Proveedor:
        p = Proveedor(nombre=nombre, telefono=telefono,
                      direccion=direccion, nota=nota)
        self.session.add(p)
        self.session.commit()
        self.session.refresh(p)
        return p

    def listar(self) -> list[Proveedor]:
        stmt = select(Proveedor).where(Proveedor.activo == True).order_by(Proveedor.nombre)  # noqa
        return list(self.session.execute(stmt).scalars())

    def obtener(self, proveedor_id: int) -> Proveedor | None:
        return self.session.get(Proveedor, proveedor_id)