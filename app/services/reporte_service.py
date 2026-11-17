from __future__ import annotations
from datetime import date

from app.repositories.reporte_repo import ReporteRepository


class ReporteService:
    def __init__(self, repo: ReporteRepository):
        self.repo = repo

    def ventas_dia(self, fecha: date | None = None) -> dict:
        if fecha is None:
            fecha = date.today()

        ventas = self.repo.ventas_del_dia(fecha)
        abonos = self.repo.abonos_del_dia(fecha)

        total_usd = 0.0
        total_cup = 0.0
        total_efectivo_cup = 0.0
        por_tipo_pago: dict[str, dict] = {}
        productos: dict[int, dict] = {}

        for v in ventas:
            v_usd = float(v.total)
            v_cup = float(v.total_cup) if v.total_cup else 0.0
            total_usd += v_usd
            total_cup += v_cup

            tipo = v.tipo_pago or "efectivo"
            if tipo not in por_tipo_pago:
                por_tipo_pago[tipo] = {
                    "cantidad": 0,
                    "total_usd": 0.0,
                    "total_cup": 0.0,
                }
            por_tipo_pago[tipo]["cantidad"] += 1
            por_tipo_pago[tipo]["total_usd"] += v_usd
            por_tipo_pago[tipo]["total_cup"] += v_cup

            # Solo efectivo cuenta para el arqueo de caja
            if tipo == "efectivo":
                total_efectivo_cup += v_cup

            # Acumular productos vendidos
            for linea in v.lineas:
                pid = linea.producto_id
                nombre = linea.producto.nombre if linea.producto else f"Producto {pid}"
                if pid not in productos:
                    productos[pid] = {
                        "nombre": nombre,
                        "cantidad": 0,
                        "total_usd": 0.0,
                        "total_cup": 0.0,
                    }
                cantidad = int(linea.cantidad)
                sub_usd = float(linea.subtotal)
                tasa_venta = float(linea.tasa_venta) if linea.tasa_venta else 0.0
                sub_cup = sub_usd * tasa_venta

                productos[pid]["cantidad"] += cantidad
                productos[pid]["total_usd"] += sub_usd
                productos[pid]["total_cup"] += sub_cup

        # Abonos en efectivo del día → también entran al cajón
        abonos_efectivo_cup = 0.0
        abonos_efectivo_count = 0
        for a in abonos:
            if (a.tipo_pago or "efectivo") == "efectivo":
                abonos_efectivo_cup += float(a.monto)
                abonos_efectivo_count += 1

        total_efectivo_cup += abonos_efectivo_cup

        return {
            "fecha": fecha.isoformat(),
            "total_ventas": len(ventas),
            "total_usd": round(total_usd, 2),
            "total_cup": round(total_cup, 2),
            "total_efectivo_cup": round(total_efectivo_cup, 2),
            "abonos_efectivo": {
                "cantidad": abonos_efectivo_count,
                "total_cup": round(abonos_efectivo_cup, 2),
            },
            "por_tipo_pago": {
                k: {
                    "cantidad": v["cantidad"],
                    "total_usd": round(v["total_usd"], 2),
                    "total_cup": round(v["total_cup"], 2),
                }
                for k, v in por_tipo_pago.items()
            },
            "productos": [
                {
                    "nombre": p["nombre"],
                    "cantidad": p["cantidad"],
                    "total_usd": round(p["total_usd"], 2),
                    "total_cup": round(p["total_cup"], 2),
                }
                for p in sorted(productos.values(), key=lambda x: x["total_cup"], reverse=True)
            ],
        }