from __future__ import annotations
from datetime import datetime, date, time
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.models import Venta, LineaVenta, Producto, Abono


class ReporteRepository:
    def __init__(self, session: Session):
        self.session = session

    def ventas_del_dia(self, fecha: date) -> list[Venta]:
        inicio = datetime.combine(fecha, time.min)
        fin = datetime.combine(fecha, time.max)
        stmt = (
            select(Venta)
            .where(Venta.fecha >= inicio, Venta.fecha <= fin)
            .order_by(Venta.fecha)
        )
        return list(self.session.execute(stmt).scalars())

    def abonos_del_dia(self, fecha: date) -> list[Abono]:
        inicio = datetime.combine(fecha, time.min)
        fin = datetime.combine(fecha, time.max)
        stmt = (
            select(Abono)
            .where(Abono.fecha >= inicio, Abono.fecha <= fin)
            .order_by(Abono.fecha)
        )
        return list(self.session.execute(stmt).scalars())