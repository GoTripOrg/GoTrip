"""Capa API: autenticación. Solo recibe la petición, llama al servicio y devuelve la respuesta.
Los errores los atiende GlobalException (carpeta global_exception)."""
from typing import Optional

from fastapi import APIRouter, Body, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from domain.auth_domain import MSG_CREDENCIALES_FALTAN, LoginRequest, RespuestaLogin
from domain.usuario_domain import MSG_MODO
from global_exception import GlobalException
from repository.auth_repository import auth_repository
from repository.usuario_repository import usuario_repository
from service.auth_services import MSG_EXITO, AuthService

router = APIRouter(prefix="/auth", tags=["MOD-04 · Usuarios y acceso"])
service = AuthService(repo_usuarios=usuario_repository, repo_auth=auth_repository)

MSG_503 = "No fue posible iniciar sesión. Intente de nuevo más tarde"


def _ejemplo(summary: str, description: str, value: dict) -> dict:
    return {"summary": summary, "description": description, "value": value}


LAURA = {"correo": "laura@correo.com", "contrasena": "Clave1234"}
CARLOS = {"correo": "carlos.mejia@correo.com", "contrasena": "Clave1234"}

# Un ejemplo por cada caso de prueba del documento HU-023 (desplegable «Examples» de Swagger).
# Antes de empezar se ejecutan los casos 1 y 2 de HU-022 (cuentas de Laura y Carlos).
EJEMPLOS = {
    "caso_01": _ejemplo("Caso 1 · Inicio de sesión exitoso como viajero (HTTP 200)",
                        "Esperado: HTTP 200 · «Inicio de sesión exitoso».",
                        {**LAURA, "modo_uso": "viajero"}),
    "caso_02": _ejemplo("Caso 2 · Inicio de sesión exitoso como proveedor (HTTP 200)",
                        "Esperado: HTTP 200 · «Inicio de sesión exitoso».",
                        {**CARLOS, "modo_uso": "proveedor"}),
    "caso_03": _ejemplo("Caso 3 · Contraseña incorrecta (HTTP 401)",
                        "Esperado: HTTP 401 · «Correo o contraseña incorrectos».",
                        {"correo": "laura@correo.com", "contrasena": "Clave9999", "modo_uso": "viajero"}),
    "caso_04": _ejemplo("Caso 4 · Correo inexistente (HTTP 401)",
                        "Esperado: HTTP 401 · «Correo o contraseña incorrectos» (igual al caso 3).",
                        {"correo": "noexiste@correo.com", "contrasena": "Clave1234", "modo_uso": "viajero"}),
    "caso_05": _ejemplo("Caso 5 · Campos obligatorios faltantes (HTTP 400)",
                        "Esperado: HTTP 400 · «Debe ingresar el correo y la contraseña».",
                        {"correo": "laura@correo.com", "modo_uso": "viajero"}),
    "caso_06": _ejemplo("Caso 6 · Modo de uso inválido (HTTP 400)",
                        "Esperado: HTTP 400 · «El modo de uso no es válido. Escoja viajero o proveedor».",
                        {**LAURA, "modo_uso": "administrador"}),
    "caso_07a": _ejemplo("Caso 7 (paso 1) · Contraseña errada de Carlos: ejecutar 3 veces (HTTP 401)",
                         "Esperado en cada intento: HTTP 401 · «Correo o contraseña incorrectos».",
                         {"correo": "carlos.mejia@correo.com", "contrasena": "Clave9999", "modo_uso": "proveedor"}),
    "caso_07b": _ejemplo("Caso 7 (paso 2) y caso 8 · Contraseña correcta de Carlos (HTTP 429 / 200)",
                         "Caso 7, justo después de los 3 fallos: HTTP 429 con el encabezado Retry-After. "
                         "Caso 8, después de que vence el bloqueo: HTTP 200.",
                         {**CARLOS, "modo_uso": "proveedor"}),
    "caso_09": _ejemplo("Caso 9 · Cuenta inactiva (HTTP 403)",
                        "Esperado: HTTP 403 · «La cuenta está inactiva y no puede iniciar sesión».",
                        {"correo": "inactivo@correo.com", "contrasena": "Clave1234", "modo_uso": "viajero"}),
    "caso_10": _ejemplo("Caso 10 · Modo no activado (HTTP 403)",
                        "Esperado: HTTP 403 · «El modo de uso elegido no está activado en su cuenta».",
                        {**LAURA, "modo_uso": "proveedor"}),
    "caso_11": _ejemplo("Caso 11 · Falla de base de datos (HTTP 503)",
                        "Esperado: HTTP 503 · «No fue posible iniciar sesión. Intente de nuevo más tarde». "
                        "Escriba en el campo X-Simular-Falla el valor «bd».",
                        {**LAURA, "modo_uso": "viajero"}),
    "caso_14": _ejemplo("Caso 14 · Error inesperado del servidor (HTTP 500)",
                        "Esperado: HTTP 500 · «Ocurrió un error inesperado. Intente de nuevo más tarde». "
                        "Escriba en el campo X-Simular-Falla el valor «error».",
                        {**LAURA, "modo_uso": "viajero"}),
}


@router.post(
    "/login", status_code=200, response_model=RespuestaLogin, summary="HU-023 · Iniciar sesión",
    dependencies=[Depends(GlobalException.exigir_json), Depends(GlobalException.simular_falla(MSG_503))],
)
@GlobalException.mensajes({"correo": MSG_CREDENCIALES_FALTAN, "contrasena": MSG_CREDENCIALES_FALTAN,
                           "modo_uso": MSG_MODO})
def iniciar_sesion(datos: LoginRequest = Body(..., openapi_examples=EJEMPLOS)):
    """Valida el correo y la contraseña, que la cuenta esté **activa** (RN-02) y que el modo elegido
    esté habilitado. Entrega un token de acceso de 24 horas. Tras 3 intentos fallidos seguidos con el
    mismo correo, el inicio de sesión se bloquea temporalmente (5, 15, 30 y 60 minutos)."""
    return RespuestaLogin(mensaje=MSG_EXITO, data=service.iniciar_sesion(datos), success=True)


# ── Sesión para los endpoints protegidos (botón «Authorize» de Swagger) ─────
bearer = HTTPBearer(auto_error=False, description="Pegue el `token_acceso` que entrega POST /api/v1/auth/login.")


def usuario_autenticado(credenciales: Optional[HTTPAuthorizationCredentials] = Depends(bearer)):
    """Dependencia: usuario de la sesión del token Bearer; si no es válida responde 401."""
    return service.usuario_de_token(credenciales.credentials if credenciales else None)
