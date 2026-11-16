from __future__ import annotations 
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Producto


class ProductoRepository:
    def __init__(self, session: Session):
        self.session = session

    def crear(self, nombre: str, precio_costo: float, precio_dueno: float,
              precio_vendedor: float, precio_cliente: float, stock: int = 0,
              stock_minimo: int = 5, descripcion: str | None = None,
              categoria: str | None = None, imagen: str | None = None) -> Producto:
        p = Producto(
            nombre=nombre,
            precio_costo=precio_costo,
            precio_dueno=precio_dueno,
            precio_vendedor=precio_vendedor,
            precio_cliente=precio_cliente,
            stock=stock,
            stock_minimo=stock_minimo,
            descripcion=descripcion,
            categoria=categoria,
            imagen=imagen,
        )
        self.session.add(p)
        self.session.commit()
        self.session.refresh(p)
        return p
    
    def listar(self) -> list[Producto]:
        stmt = select(Producto).where(Producto.activo == True).order_by(Producto.nombre)  # noqa
        return list(self.session.execute(stmt).scalars())

    def obtener(self, producto_id: int) -> Producto | None:
        return self.session.get(Producto, producto_id)

    def actualizar(self, producto_id: int, **campos) -> Producto | None:
        p = self.obtener(producto_id)
        if not p:
            return None
        for k, v in campos.items():
            if hasattr(p, k) and v is not None:
                setattr(p, k, v)
        self.session.commit()
        self.session.refresh(p)
        return p

    def desactivar(self, producto_id: int) -> bool:
        p = self.obtener(producto_id)
        if not p:
            return False
        p.activo = False
        self.session.commit()
        return True

    def actualizar_costo(self, producto_id: int, nuevo_costo: float) -> None:
        p = self.obtener(producto_id)
        if p:
            p.precio_costo = nuevo_costo
            self.session.commit()
