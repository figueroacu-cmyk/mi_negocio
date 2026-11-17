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
            total_cup=0,
        )

        self.session.add(compra)
        self.session.flush()  # para tener compra.id

        total = 0.0
        for ln in lineas:
            producto_id = ln.get("producto_id")
            cantidad = int(ln["cantidad"])
            precio_compra = float(ln["precio_compra"])

            if producto_id:
                # Producto existente: solo actualizar stock y costo ponderado
                producto = self.session.get(Producto, producto_id)
                if not producto:
                    raise ValueError(f"Producto {producto_id} no encontrado")
                if not producto.activo:
                    raise ValueError(f"Producto {producto.nombre} está inactivo")

                stock_actual = max(int(producto.stock), 0)
                costo_actual = float(producto.precio_costo)

                # Promedio ponderado
                if stock_actual + cantidad > 0:
                    nuevo_costo = (
                        stock_actual * costo_actual + cantidad * precio_compra
                    ) / (stock_actual + cantidad)
                else:
                    nuevo_costo = precio_compra

                producto.precio_costo = round(nuevo_costo, 2)
                producto.stock = stock_actual + cantidad
                producto.tasa_compra = tasa_cambio
            else:
                # Producto nuevo creado al vuelo desde el formulario de compra
                precio_dueno = float(ln.get("precio_dueno", 0))
                precio_vendedor = float(ln.get("precio_vendedor", 0))
                producto = Producto(
                    nombre=ln["producto_nombre"],
                    precio_costo=precio_compra,
                    precio_dueno=precio_dueno,
                    precio_vendedor=precio_vendedor,
                    precio_cliente=precio_dueno + precio_vendedor,
                    stock=cantidad,
                    tasa_compra=tasa_cambio,
                )
                self.session.add(producto)
                self.session.flush()
                producto_id = producto.id

            subtotal = cantidad * precio_compra

            linea = LineaCompra(
                compra_id=compra.id,
                producto_id=producto_id,
                cantidad=cantidad,
                precio_compra=precio_compra,
                subtotal=subtotal,
            )
            self.session.add(linea)
            total += subtotal

        compra.total = total
        compra.total_cup = round(total * tasa_cambio, 2)
        self.session.commit()
        self.session.refresh(compra)
        return compra
    
    def listar(self) -> list[Compra]:
        stmt = select(Compra).order_by(Compra.fecha.desc())
        return list(self.session.execute(stmt).scalars())

    def obtener(self, compra_id: int) -> Compra | None:
        return self.session.get(Compra, compra_id)
