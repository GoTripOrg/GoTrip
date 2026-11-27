"""Dominio: parámetros globales del sistema (HU-018). Sin FastAPI ni acceso a datos.
Se cargan con el script semilla y los demás módulos los consumen en solo lectura (RN-18)."""
from typing import Union

from pydantic import BaseModel

CATEGORIAS = ("operacion", "seguridad", "notificaciones")
TIPOS_DATO = {"string": str, "int": int, "double": float, "boolean": bool, "date": str}
MSG_CATEGORIA = "La categoría indicada no es válida. Use operacion, seguridad o notificaciones"


class Parametro:
    def __init__(self, codigo: str, nombre: str, tipo_dato: str, valor, ambito: str, categoria: str,
                 estado: str = "activo"):
        # REGLA: el valor se guarda con el tipo nativo que indica tipo_dato
        if tipo_dato not in TIPOS_DATO or type(valor) is not TIPOS_DATO[tipo_dato]:
            raise ValueError(f"El valor del parámetro {codigo} no corresponde a su tipo de dato")
        if categoria not in CATEGORIAS:
            raise ValueError(MSG_CATEGORIA)
        self.codigo = codigo
        self.nombre = nombre
        self.tipo_dato = tipo_dato
        self.valor = valor
        self.ambito = ambito
        self.categoria = categoria
        self.estado = estado

    def to_response(self) -> dict:
        return {"codigo": self.codigo, "nombre": self.nombre, "tipo_dato": self.tipo_dato, "valor": self.valor,
                "ambito": self.ambito, "categoria": self.categoria, "estado": self.estado}


class ParametroResponse(BaseModel):
    """Un parámetro global; `valor` conserva su tipo JSON (número, booleano o texto)."""
    codigo: str
    nombre: str
    tipo_dato: str
    valor: Union[bool, int, float, str]
    ambito: str
    categoria: str
    estado: str


class RespuestaParametros(BaseModel):
    """Envoltorio de la respuesta exitosa de HU-018."""
    mensaje: str
    data: list[ParametroResponse]
    success: bool
