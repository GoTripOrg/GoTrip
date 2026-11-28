"""Capa API: roles y permisos. Solo recibe la petición, llama al servicio y devuelve la respuesta.
Los errores los atiende GlobalException (carpeta global_exception)."""
from fastapi import APIRouter, Depends, Path

from api.auth_api import usuario_autenticado
from domain.rol_domain import RespuestaRol, RespuestaRoles
from global_exception import MSG_500, MSG_ID, GlobalException
from repository.rol_repository import rol_repository
from service.auth_services import MSG_SESION_INVALIDA
from service.rol_services import MSG_EXITO, MSG_NO_EXISTE, MSG_SIN_PERMISO, RolService

router = APIRouter(prefix="/roles", tags=["MOD-04 · Usuarios y acceso"])
service = RolService(repo=rol_repository)

MSG_503 = "No fue posible consultar los roles. Intente de nuevo más tarde"


def con_permiso_de_consulta(usuario=Depends(usuario_autenticado)):
    """Dependencia: sesión válida (401) y permiso ROLES_CONSULTAR (403), antes de leer la ruta."""
    service.verificar_permiso_consulta(usuario)
    return usuario


def _error(mensaje: str) -> dict:
    return {"mensaje": mensaje, "data": None, "success": False}


_GESTOR = {"id_rol": 4, "nombre": "Gestor de soporte", "tipo": "interno",
           "permisos": [{"codigo": "PARAMETROS_CONSULTAR", "descripcion": "Consultar parámetros globales"}]}
_COMUNES = {
    401: {"description": "Sin token, o token inválido, vencido o cerrado.",
          "content": {"application/json": {"example": _error(MSG_SESION_INVALIDA)}}},
    403: {"description": "Rol sin permiso (por ejemplo, Viajero).",
          "content": {"application/json": {"example": _error(MSG_SIN_PERMISO)}}},
    503: {"description": "Falla de base de datos (X-Simular-Falla = bd).",
          "content": {"application/json": {"example": _error(MSG_503)}}},
    500: {"description": "Error inesperado del servidor (X-Simular-Falla = error).",
          "content": {"application/json": {"example": _error(MSG_500)}}},
}
RESPUESTAS_LISTA = {
    200: {"description": "Caso 1 · Lista de los siete roles.",
          "content": {"application/json": {"example": {"mensaje": MSG_EXITO, "data": [_GESTOR], "success": True}}}},
    **_COMUNES,
}
RESPUESTAS_DETALLE = {
    200: {"description": "Caso 2 · Detalle del rol 4.",
          "content": {"application/json": {"example": {"mensaje": MSG_EXITO, "data": _GESTOR, "success": True}}}},
    400: {"description": "Caso 7 · Identificador no numérico, cero o negativo.",
          "content": {"application/json": {"example": _error(MSG_ID)}}},
    404: {"description": "Caso 3 · Rol inexistente.", "content": {"application/json": {"example": _error(MSG_NO_EXISTE)}}},
    **_COMUNES,
}
DEPENDENCIAS = [Depends(GlobalException.simular_falla(MSG_503)), Depends(con_permiso_de_consulta)]


@router.get("", response_model=RespuestaRoles, summary="HU-026 · Consultar roles y permisos (lista)",
            responses=RESPUESTAS_LISTA, dependencies=DEPENDENCIAS)
def consultar_roles():
    """Requiere **token de acceso** de Administrador (botón *Authorize*). Devuelve los siete roles con su tipo
    (`modo_uso` o `interno`) y sus permisos fijos. Los roles y permisos solo se leen; se cargan con el script semilla."""
    return RespuestaRoles(mensaje=MSG_EXITO, data=service.consultar(), success=True)


@router.get("/{id_rol}", response_model=RespuestaRol, summary="HU-026 · Consultar roles y permisos (detalle)",
            responses=RESPUESTAS_DETALLE, dependencies=DEPENDENCIAS)
def consultar_rol(id_rol: int = Path(..., gt=0, description="Identificador del rol (entero positivo)")):
    """Requiere **token de acceso** de Administrador (botón *Authorize*). Devuelve un rol con sus permisos;
    si no existe responde 404."""
    return RespuestaRol(mensaje=MSG_EXITO, data=service.obtener(id_rol), success=True)
