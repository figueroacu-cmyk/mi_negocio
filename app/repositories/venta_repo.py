from __future__ import annotations 
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Venta, LineaVenta, Producto, Abono


class VentaRepository:
    def __init__(self, session: Session):
        self.session = session

    def crear(self, cliente_id, fecha, nota, tipo_pago, lineas,
              abono_inicial=0, tipo_pago_abono=None, tasa_cambio=0) -> Venta:
        from app.db.models import Venta, LineaVenta, Producto, Abono
        from datetime import datetime

        venta = Venta(
            cliente_id=cliente_id,
            fecha=fecha or datetime.now(),
            nota=nota,
            tipo_pago=tipo_pago,
            estado="pagada",
            total=0,
            total_cup=0,
            tasa_cambio=tasa_cambio,   # ← LÍNEA QUE FALTABA
        )
        self.session.add(venta)
        self.session.flush()

        total = 0.0
        for ln in lineas:
            producto = self.session.get(Producto, ln["producto_id"])
            if not producto:
                raise ValueError(f"Producto {ln['producto_id']} no encontrado")
            if producto.stock < ln["cantidad"]:
                raise ValueError(f"Stock insuficiente para {producto.nombre}")

            cantidad = int(ln["cantidad"])
            precio_dueno = float(ln["precio_dueno"])
            precio_vendedor = float(ln["precio_vendedor"])
            precio_cliente = float(ln["precio_cliente"])
            subtotal = cantidad * precio_cliente

            linea = LineaVenta(
                venta_id=venta.id,
                producto_id=producto.id,
                cantidad=cantidad,
                precio_dueno=precio_dueno,
                precio_vendedor=precio_vendedor,
                precio_cliente=precio_cliente,
                subtotal=subtotal,
                precio_costo_usd=float(producto.precio_costo),
                tasa_compra=float(producto.tasa_compra),
                tasa_venta=tasa_cambio,
            )
            self.session.add(linea)

            producto.stock -= cantidad
            total += subtotal

        venta.total = total
        venta.total_cup = total * tasa_cambio
        
        if abono_inicial and abono_inicial > 0:
            abono = Abono(
                venta_id=venta.id,
                monto=abono_inicial,
                tipo_pago=tipo_pago_abono or "efectivo",
            )
            self.session.add(abono)

        self.session.commit()
        self.session.refresh(venta)
        return venta

    def listar(self) -> list[Venta]:
        stmt = select(Venta).order_by(Venta.fecha.desc())
        return list(self.session.execute(stmt).scalars())

    def obtener(self, venta_id: int) -> Venta | None:
        return self.session.get(Venta, venta_id)

    def listar_pendientes_por_cliente(self, cliente_id: int) -> list[Venta]:
        stmt = select(Venta).where(
            Venta.cliente_id == cliente_id,
            Venta.estado == "pendiente",
        ).order_by(Venta.fecha)
        return list(self.session.execute(stmt).scalars())

    def abonar(self, venta_id: int, monto: float,
               tipo_pago: str, nota: str | None) -> Abono:
        venta = self.session.get(Venta, venta_id)
        if not venta:
            raise ValueError("Venta no encontrada")
        if venta.estado != "pendiente":
            raise ValueError("Esta venta no tiene saldo pendiente")
        if monto <= 0:
            raise ValueError("El monto debe ser mayor que cero")
        if monto > venta.saldo + 0.001:
            raise ValueError(f"El monto excede el saldo pendiente ({venta.saldo})")

        abono = Abono(
            venta_id=venta.id,
            monto=monto,
            tipo_pago=tipo_pago,
            nota=nota,
        )
        self.session.add(abono)
        self.session.flush()

        if venta.saldo <= 0.001:
            venta.estado = "pagada"

        self.session.commit()
        self.session.refresh(abono)
        return abono
