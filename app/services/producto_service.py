from __future__ import annotations 
from app.repositories.producto_repo import ProductoRepository


class ProductoService:
    def __init__(self, repo: ProductoRepository):
        self.repo = repo

    def crear(self, nombre: str, precio_costo: float, precio_dueno: float,
              precio_vendedor: float, precio_cliente: float, stock: int = 0,
              stock_minimo: int = 5, descripcion: str | None = None,
              categoria: str | None = None, imagen: str | None = None):
        if not nombre:
            raise ValueError("Nombre obligatorio")
        if precio_costo < 0 or precio_dueno < 0 or precio_vendedor < 0 or precio_cliente < 0:
            raise ValueError("Los precios no pueden ser negativos")
        return self.repo.crear(nombre, precio_costo, precio_dueno, precio_vendedor,
                               precio_cliente, stock, stock_minimo, descripcion,
                               categoria, imagen)
    
    def listar(self):
        return self.repo.listar()

    def obtener(self, producto_id: int):
        p = self.repo.obtener(producto_id)
        if not p or not p.activo:
            raise ValueError("Producto no encontrado")
        return p

    def actualizar(self, producto_id: int, **campos):
        for key in ("precio_costo", "precio_dueno", "precio_vendedor", "precio_cliente"):
            if key in campos and campos[key] is not None and campos[key] < 0:
                raise ValueError("Los precios no pueden ser negativos")
        if "nombre" in campos and not campos["nombre"]:
            raise ValueError("El nombre no puede estar vacío")
        p = self.repo.actualizar(producto_id, **campos)
        if not p:
            raise ValueError("Producto no encontrado")
        return p
    
    def desactivar(self, producto_id: int):
        if not self.repo.desactivar(producto_id):
            raise ValueError("Producto no encontrado")
