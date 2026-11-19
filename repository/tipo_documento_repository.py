"""Repositorio en memoria de tipos de documento (catálogo fijo; datos semilla de HU-006)."""
from typing import Optional

from domain.tipo_documento_domain import TipoDocumento


class TipoDocumentoRepository:
    def __init__(self):
        self._datos: list = []
        self._seed()

    def _seed(self):
        # Los demás tipos (cédula de extranjería, NIT, pasaporte) están pendientes de verificar (HU-006).
        self._datos = [
            TipoDocumento(1, "CC", "Cédula de ciudadanía", "^[0-9]{1,10}$"),
            TipoDocumento(2, "TI", "Tarjeta de identidad", "^[0-9]{10,11}$"),
        ]

    def obtener_todos(self) -> list:
        return list(self._datos)

    def obtener_por_id(self, id_tipo_documento: int) -> Optional[TipoDocumento]:
        return next((t for t in self._datos if t.id_tipo_documento == id_tipo_documento), None)


tipo_documento_repository = TipoDocumentoRepository()
