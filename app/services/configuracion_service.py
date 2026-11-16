from app.repositories.configuracion_repo import ConfiguracionRepository


class ConfiguracionService:
    def __init__(self, repo: ConfiguracionRepository):
        self.repo = repo

    def obtener(self):
        return self.repo.obtener()

    def actualizar_tasa(self, nueva_tasa: float):
        if nueva_tasa <= 0:
            raise ValueError("La tasa de cambio debe ser mayor que cero")
        return self.repo.actualizar_tasa(nueva_tasa)