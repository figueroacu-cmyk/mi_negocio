from app.repositories.venta_repo import VentaRepository
from app.repositories.producto_repo import ProductoRepository
from app.repositories.cliente_repo import ClienteRepository
from app.repositories.configuracion_repo import ConfiguracionRepository

class VentaService:
    def __init__(self, venta_repo: VentaRepository,
                 producto_repo: ProductoRepository,
                 cliente_repo: ClienteRepository,
                 config_repo: ConfiguracionRepository):
        self.venta_repo = venta_repo
        self.producto_repo = producto_repo
        self.cliente_repo = cliente_repo
        self.config_repo = config_repo
        
    def registrar(self, cliente_id, fecha, nota, tipo_pago, lineas,
                  abono_inicial=0, tipo_pago_abono=None):
        if not lineas:
            raise ValueError("La venta debe tener al menos una línea")
        if tipo_pago not in ("efectivo", "transferencia", "credito"):
            raise ValueError("Tipo de pago inválido")

        for ln in lineas:
            if not ln.get("producto_id"):
                raise ValueError("Cada línea debe tener un producto")
            if int(ln.get("cantidad", 0)) <= 0:
                raise ValueError("La cantidad debe ser mayor que cero")
            if (float(ln.get("precio_dueno", -1)) < 0 or
                float(ln.get("precio_vendedor", -1)) < 0 or
                float(ln.get("precio_cliente", -1)) < 0):
                raise ValueError("Los precios no pueden ser negativos")

        if tipo_pago == "credito":
            if not cliente_id:
                raise ValueError("Una venta a crédito requiere un cliente registrado")
            if abono_inicial and abono_inicial > 0 and not tipo_pago_abono:
                raise ValueError("Debe indicar el tipo de pago del abono inicial")

        # La tasa la define el dueño en Configuracion, una vez al día
        tasa_cambio = float(self.config_repo.obtener().tasa_cambio)
        if tasa_cambio <= 0:
            raise ValueError("La tasa de cambio no está configurada correctamente")

        return self.venta_repo.crear(
            cliente_id=cliente_id,
            fecha=fecha,
            nota=nota,
            tipo_pago=tipo_pago,
            lineas=lineas,
            abono_inicial=abono_inicial or 0,
            tipo_pago_abono=tipo_pago_abono,
            tasa_cambio=tasa_cambio,
        )
    
    def listar(self):
        return self.venta_repo.listar()

    def obtener(self, venta_id):
        v = self.venta_repo.obtener(venta_id)
        if not v:
            raise ValueError("Venta no encontrada")
        return v

    def abonar(self, venta_id, monto, tipo_pago, nota):
        if tipo_pago not in ("efectivo", "transferencia"):
            raise ValueError("Tipo de pago del abono inválido")
        return self.venta_repo.abonar(venta_id, monto, tipo_pago, nota)
