from sqlalchemy.orm import Session

from app.db.models import Configuracion


class ConfiguracionRepository:
    def __init__(self, session: Session):
        self.session = session

    def obtener(self) -> Configuracion:
        config = self.session.get(Configuracion, 1)
        if not config:
            config = Configuracion(id=1, tasa_cambio=320.00)
            self.session.add(config)
            self.session.commit()
            self.session.refresh(config)
        return config

    def actualizar_tasa(self, nueva_tasa: float) -> Configuracion:
        config = self.obtener()
        config.tasa_cambio = nueva_tasa
        self.session.commit()
        self.session.refresh(config)
        return config