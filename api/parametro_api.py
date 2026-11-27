"""Capa API: parámetros globales. Solo recibe la petición, llama al servicio y devuelve la respuesta.
Los errores los atiende GlobalException (carpeta global_exception)."""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from api.auth_api import usuario_autenticado
from domain.parametro_domain import MSG_CATEGORIA, RespuestaParametros
from global_exception import MSG_500, GlobalException
from repository.parametro_repository import parametro_repository
from repository.rol_repository import rol_repository
from service.auth_services import MSG_SESION_INVALIDA
from service.parametro_services import MSG_EXITO, MSG_SIN_PERMISO, MSG_VACIO, ParametroService

router = APIRouter(prefix="/parametros-globales", tags=["MOD-01 · Parámetros y configuración"])
service = ParametroService(repo=parametro_repository, repo_roles=rol_repository)

MSG_503 = "No fue posible consultar los parámetros globales"


def _error(mensaje: str) -> dict:
    return {"mensaje": mensaje, "data": None, "success": False}


# Respuestas del documento HU-018 (aparecen como ejemplos en Swagger)
RESPUESTAS = {
    200: {
        "description": "Consulta exitosa (casos 1 y 2) o sin resultados (caso 3).",
        "content": {"application/json": {"examples": {
            "caso_02": {"summary": "Caso 2 · Consulta por categoría operacion", "value": {
                "mensaje": MSG_EXITO,
                "data": [
                    {"codigo": "TIEMPO_LIBERACION_CUPO_MIN", "nombre": "Tiempo de liberación de cupo bloqueado",
                     "tipo_dato": "int", "valor": 15, "ambito": "reservas", "categoria": "operacion",
                     "estado": "activo"},
                    {"codigo": "IVA_PORCENTAJE", "nombre": "Porcentaje de IVA vigente", "tipo_dato": "double",
                     "valor": 19.0, "ambito": "pagos", "categoria": "operacion", "estado": "activo"},
                ],
                "success": True}},
            "caso_03": {"summary": "Caso 3 · Consulta sin resultados", "value": {
                "mensaje": MSG_VACIO, "data": [], "success": True}},
        }}},
    },
    400: {"description": "Caso 4 · Categoría inválida.", "content": {"application/json": {"example": _error(MSG_CATEGORIA)}}},
    401: {"description": "Caso 5 · Sin token, o token inválido, vencido o cerrado.",
          "content": {"application/json": {"example": _error(MSG_SESION_INVALIDA)}}},
    403: {"description": "Caso 6 · Rol sin permiso (Viajero).",
          "content": {"application/json": {"example": _error(MSG_SIN_PERMISO)}}},
    503: {"description": "Caso 7 · Falla de base de datos (X-Simular-Falla = bd).",
          "content": {"application/json": {"example": _error(MSG_503)}}},
    500: {"description": "Caso 8 · Error inesperado del servidor (X-Simular-Falla = error).",
          "content": {"application/json": {"example": _error(MSG_500)}}},
}


@router.get(
    "", response_model=RespuestaParametros, summary="HU-018 · Consultar parámetros globales",
    responses=RESPUESTAS, dependencies=[Depends(GlobalException.simular_falla(MSG_503))],
)
def consultar_parametros_globales(
        categoria: Optional[str] = Query(
            None, description="Opcional: `operacion`, `seguridad` o `notificaciones`. Déjelo vacío para ver todos."),
        usuario=Depends(usuario_autenticado)):
    """Requiere **token de acceso** (botón *Authorize*). Solo el **Administrador** y el **Gestor de soporte**
    tienen el permiso de consulta. Devuelve los parámetros vigentes cargados con el script semilla; la
    aplicación no permite crearlos ni modificarlos (RN-18)."""
    mensaje, data = service.consultar(usuario, categoria)
    return RespuestaParametros(mensaje=mensaje, data=data, success=True)
