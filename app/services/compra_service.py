from __future__ import annotations 
from app.repositories.compra_repo import CompraRepository
from app.repositories.producto_repo import ProductoRepository
from app.repositories.proveedor_repo import ProveedorRepository


class CompraService:
    def __init__(self, compra_repo: CompraRepository,
                 producto_repo: ProductoRepository,
                 proveedor_repo: ProveedorRepository):
        self.compra_repo = compra_repo
        self.producto_repo = producto_repo
        self.proveedor_repo = proveedor_repo

    def registrar(self, proveedor_id: int | None, numero_factura: str | None,
                  nota: str | None, lineas: list[dict], fecha=None):
        if not lineas:
            raise ValueError("La compra debe tener al menos una línea")
        for ln in lineas:
            if not ln.get("producto_id") and not ln.get("producto_nombre"):
                raise ValueError("Cada línea debe tener producto o nombre de producto nuevo")
            if int(ln.get("cantidad", 0)) <= 0:
                raise ValueError("La cantidad debe ser mayor que cero")
            if float(ln.get("precio_compra", -1)) < 0:
                raise ValueError("El precio de compra no puede ser negativo")
        return self.compra_repo.crear(proveedor_id, numero_factura, nota,
                                      lineas, fecha, tasa_cambio)
    def listar(self):
        return self.compra_repo.listar()

    def obtener(self, compra_id: int):
        c = self.compra_repo.obtener(compra_id)
        if not c:
            raise ValueError("Compra no encontrada")
        return c
