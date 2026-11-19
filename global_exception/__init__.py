"""Manejo global de errores: se importa como `from global_exception import GlobalException, Conflicto, ...`."""
from global_exception.global_exception import (  # noqa: F401
    GlobalException, ErrorNegocio, Invalido, NoAutenticado, SinPermiso, NoEncontrado, Conflicto,
    TipoContenido, NoDisponible, MSG_500, MSG_ID, MSG_JSON, MSG_OBLIGATORIOS, MSG_TIPO, MSG_EXTRA,
    MSG_LARGO, MSG_CONTENT_TYPE)
