"""Capa API: rutas de tipos de documento. Solo recibe la petición, llama al servicio y devuelve la respuesta.
Los errores los atiende GlobalException (carpeta global_exception)."""
from fastapi import APIRouter, Depends

from domain.tipo_documento_domain import RespuestaTiposDocumento
from global_exception import MSG_500, GlobalException
from repository.tipo_documento_repository import tipo_documento_repository
from service.tipo_documento_services import TipoDocumentoService

router = APIRouter(prefix="/tipos-documento", tags=["MOD-01 · Parámetros y configuración"])
service = TipoDocumentoService(repo=tipo_documento_repository)

MSG_503 = "No fue posible consultar los tipos de documento"


def _error(mensaje: str) -> dict:
    return {"mensaje": mensaje, "data": None, "success": False}


# Respuestas del documento HU-006 (aparecen como ejemplos en Swagger)
RESPUESTAS = {
    200: {
        "description": "Consulta exitosa (caso 1) o catálogo vacío (caso 3).",
        "content": {"application/json": {"examples": {
            "caso_01": {"summary": "Caso 1 · Consulta con tipos registrados", "value": {
                "mensaje": "Consulta de tipos de documento exitosa",
                "data": [
                    {"id_tipo_documento": 1, "codigo": "CC", "nombre": "Cédula de ciudadanía",
                     "formato_validacion": "^[0-9]{1,10}$"},
                    {"id_tipo_documento": 2, "codigo": "TI", "nombre": "Tarjeta de identidad",
                     "formato_validacion": "^[0-9]{10,11}$"},
                ],
                "success": True}},
            "caso_03": {"summary": "Caso 3 · Consulta sin registros", "value": {
                "mensaje": "No hay tipos de documento registrados", "data": [], "success": True}},
        }}},
    },
    503: {"description": "Caso 5 · Falla de base de datos (X-Simular-Falla = bd).",
          "content": {"application/json": {"example": _error(MSG_503)}}},
    500: {"description": "Caso 6 · Error inesperado del servidor (X-Simular-Falla = error).",
          "content": {"application/json": {"example": _error(MSG_500)}}},
}


@router.get(
    "", response_model=RespuestaTiposDocumento, summary="HU-006 · Consultar tipos de documento",
    responses=RESPUESTAS, dependencies=[Depends(GlobalException.simular_falla(MSG_503))],
)
def consultar_tipos_documento():
    """Endpoint **público** (sin token). Devuelve el catálogo de tipos de documento ordenado por nombre,
    con el formato de validación de cada número. El catálogo es de solo lectura (RN-18)."""
    mensaje, data = service.consultar()
    return RespuestaTiposDocumento(mensaje=mensaje, data=data, success=True)
