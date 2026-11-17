from __future__ import annotations
from app.repositories.compra_repo import CompraRepository
from app.repositories.producto_repo import ProductoRepository
from app.repositories.proveedor_repo import ProveedorRepository
from app.repositories.configuracion_repo import ConfiguracionRepository


class CompraService:
    def __init__(self, compra_repo: CompraRepository,
                 producto_repo: ProductoRepository,
                 proveedor_repo: ProveedorRepository,
                 config_repo: ConfiguracionRepository):
        self.compra_repo = compra_repo
        self.producto_repo = producto_repo
        self.proveedor_repo = proveedor_repo
        self.config_repo = config_repo

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

            # Para producto nuevo, validar precios de venta
            if not ln.get("producto_id"):
                if not ln.get("producto_nombre", "").strip():
                    raise ValueError("El producto nuevo debe tener nombre")
                if float(ln.get("precio_dueno", -1)) < 0:
                    raise ValueError("El precio del dueño no puede ser negativo")
                if float(ln.get("precio_vendedor", -1)) < 0:
                    raise ValueError("El precio del vendedor no puede ser negativo")

        # La tasa la define el dueño en Configuracion, una vez al día
        tasa_cambio = float(self.config_repo.obtener().tasa_cambio)
        if tasa_cambio <= 0:
            raise ValueError("La tasa de cambio no está configurada correctamente")

        return self.compra_repo.crear(
            proveedor_id=proveedor_id,
            numero_factura=numero_factura,
            nota=nota,
            lineas=lineas,
            fecha=fecha,
            tasa_cambio=tasa_cambio,
        )

    def listar(self):
        return self.compra_repo.listar()

    def obtener(self, compra_id: int):
        c = self.compra_repo.obtener(compra_id)
        if not c:
            raise ValueError("Compra no encontrada")
        return c
