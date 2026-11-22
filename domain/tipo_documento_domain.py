"""Dominio: tipo de documento de identidad (catálogo fijo, HU-006)."""
import re

from pydantic import BaseModel


class TipoDocumento:
    def __init__(self, id_tipo_documento: int, codigo: str, nombre: str, formato_validacion: str):
        self.id_tipo_documento = id_tipo_documento
        self.codigo = codigo
        self.nombre = nombre
        self.formato_validacion = formato_validacion

    def numero_valido(self, numero: str) -> bool:
        """REGLA: el número cumple el formato (caracteres y tamaño) del tipo."""
        return re.fullmatch(self.formato_validacion, numero) is not None

    def to_response(self) -> dict:
        return {"id_tipo_documento": self.id_tipo_documento, "codigo": self.codigo,
                "nombre": self.nombre, "formato_validacion": self.formato_validacion}


class TipoDocumentoResponse(BaseModel):
    """Datos de un tipo de documento que devuelve la API."""
    id_tipo_documento: int
    codigo: str
    nombre: str
    formato_validacion: str


class RespuestaTiposDocumento(BaseModel):
    """Envoltorio de la respuesta exitosa de HU-006."""
    mensaje: str
    data: list[TipoDocumentoResponse]
    success: bool
