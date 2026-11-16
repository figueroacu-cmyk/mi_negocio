from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Numeric, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Producto(Base):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    descripcion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    precio_costo: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    precio_dueno: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    precio_vendedor: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    precio_cliente: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stock_minimo: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    categoria: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    imagen: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    tasa_compra: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)

class Proveedor(Base):
    __tablename__ = "proveedores"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    telefono: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    direccion: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    nota: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Compra(Base):
    __tablename__ = "compras"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    proveedor_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("proveedores.id"), nullable=True, index=True
    )
    numero_factura: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    fecha: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    nota: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    total: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    tasa_cambio: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    proveedor: Mapped[Optional[Proveedor]] = relationship()
    lineas: Mapped[List["LineaCompra"]] = relationship(
        back_populates="compra", cascade="all, delete-orphan"
    )

class LineaCompra(Base):
    __tablename__ = "lineas_compra"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    compra_id: Mapped[int] = mapped_column(ForeignKey("compras.id"), nullable=False, index=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), nullable=False, index=True)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_compra: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    compra: Mapped[Compra] = relationship(back_populates="lineas")
    producto: Mapped[Producto] = relationship()


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    telefono: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    direccion: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    nota: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # AÑADE ESTA LÍNEA:
    ventas: Mapped[List["Venta"]] = relationship(back_populates="cliente")

class Venta(Base):
    __tablename__ = "ventas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cliente_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("clientes.id"), nullable=True, index=True
    )
    fecha: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    nota: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    total: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    tasa_cambio: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total_cup: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    tipo_pago: Mapped[str] = mapped_column(String(20), nullable=False, default="efectivo")
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="pagada")

    cliente: Mapped[Optional[Cliente]] = relationship(back_populates="ventas")
    lineas: Mapped[List["LineaVenta"]] = relationship(
        back_populates="venta", cascade="all, delete-orphan"
    )
    abonos: Mapped[List["Abono"]] = relationship(
        back_populates="venta", cascade="all, delete-orphan"
    )

    @property
    def total_abonado(self) -> float:
        return sum(float(a.monto) for a in self.abonos)

    @property
    def saldo(self) -> float:
        return float(self.total) - self.total_abonado
    
class LineaVenta(Base):
    __tablename__ = "lineas_venta"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    venta_id: Mapped[int] = mapped_column(ForeignKey("ventas.id"), nullable=False, index=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), nullable=False, index=True)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_dueno: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    precio_vendedor: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    precio_cliente: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    precio_costo_usd: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    tasa_compra: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    tasa_venta: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    venta: Mapped[Venta] = relationship(back_populates="lineas")
    producto: Mapped[Producto] = relationship()
    
class Abono(Base):
    __tablename__ = "abonos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    venta_id: Mapped[int] = mapped_column(ForeignKey("ventas.id"), nullable=False, index=True)
    monto: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    tipo_pago: Mapped[str] = mapped_column(String(20), nullable=False, default="efectivo")
    nota: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)

    venta: Mapped[Venta] = relationship(back_populates="abonos")

class Configuracion(Base):
    __tablename__ = "configuracion"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    tasa_cambio: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=320.00)
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
