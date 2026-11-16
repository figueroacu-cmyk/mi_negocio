from __future__ import annotations 
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Compra, LineaCompra, Producto


class CompraRepository:
    def __init__(self, session: Session):
        self.session = session

    def crear(self, proveedor_id: int | None, numero_factura: str | None,
              nota: str | None, lineas: list[dict], fecha=None,
              tasa_cambio: float = 0) -> Compra:
        compra = Compra(
            proveedor_id=proveedor_id,
            numero_factura=numero_factura,
            nota=nota,
            fecha=fecha if fecha else datetime.now(),
            total=0,
            tasa_cambio=tasa_cambio,
        )
        
        self.session.add(compra)
        self.session.flush()  # para tener compra.id

        total = 0.0
        for ln in lineas:
            producto_id = ln.get("producto_id")
            if not producto_id:
                # Producto nuevo creado al vuelo
                nuevo = Producto(
                    nombre=ln["producto_nombre"],
                    precio=ln.get("precio_venta", 0),
                    stock=0,
                )
                self.session.add(nuevo)
                self.session.flush()
                producto_id = nuevo.id

            producto = self.session.get(Producto, producto_id)
            cantidad = int(ln["cantidad"])
            precio_compra = float(ln["precio_compra"])
            subtotal = cantidad * precio_compra

            linea = LineaCompra(
                compra_id=compra.id,
                producto_id=producto_id,
                cantidad=cantidad,
                precio_compra=precio_compra,
                subtotal=subtotal,
            )
            self.session.add(linea)

            producto.stock += cantidad
            producto.precio_costo = precio_compra
            producto.tasa_compra = tasa_cambio
            total += subtotal

        compra.total = total
        self.session.commit()
        self.session.refresh(compra)
        return compra

    def listar(self) -> list[Compra]:
        stmt = select(Compra).order_by(Compra.fecha.desc())
        return list(self.session.execute(stmt).scalars())

    def obtener(self, compra_id: int) -> Compra | None:
        return self.session.get(Compra, compra_id)
