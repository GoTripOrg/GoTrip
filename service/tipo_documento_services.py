"""Servicio de tipos de documento: orquesta dominio + repositorio. No conoce HTTP ni FastAPI."""
from repository.tipo_documento_repository import TipoDocumentoRepository

MSG_EXITO = "Consulta de tipos de documento exitosa"
MSG_VACIO = "No hay tipos de documento registrados"


class TipoDocumentoService:
    def __init__(self, repo: TipoDocumentoRepository):
        self.repo = repo

    def consultar(self) -> tuple[str, list[dict]]:
        """HU-006: catálogo completo ordenado por nombre (RN-18: solo lectura)."""
        tipos = sorted(self.repo.obtener_todos(), key=lambda t: t.nombre)
        if not tipos:
            return MSG_VACIO, []
        return MSG_EXITO, [t.to_response() for t in tipos]
