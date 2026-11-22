"""Manejo global de errores de GoTrip.

Aquí vive TODO lo que se repite en los casos de prueba de las HU:
  - los errores de negocio (el servicio los lanza, esta clase los convierte en la respuesta HTTP),
  - los mensajes comunes (campos obligatorios, JSON inválido, tipo de dato, etc.),
  - la validación de Content-Type (415) y las fallas simuladas (503 / 500),
  - el formato de error { "mensaje", "data", "success" } con el código HTTP documentado en cada HU.

Las demás capas (api, service, domain, repository) solo importan lo que necesitan de este paquete.
"""
from typing import Optional

from fastapi import FastAPI, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# ── Mensajes comunes a todas las HU ──────────────────────────────────────────
MSG_500 = "Ocurrió un error inesperado. Intente de nuevo más tarde"
MSG_ID = "El identificador indicado no tiene un formato válido"
MSG_JSON = "El cuerpo de la petición no es un JSON válido o está vacío"
MSG_OBLIGATORIOS = "Hay campos obligatorios sin diligenciar"
MSG_TIPO = "Uno de los campos tiene un tipo de dato incorrecto"
MSG_EXTRA = "La petición contiene campos no permitidos"
MSG_LARGO = "Uno de los campos supera la longitud máxima permitida"
MSG_CONTENT_TYPE = "El tipo de contenido debe ser application/json"


# ── Errores de negocio: el servicio lanza uno y GlobalException responde con su código ──
class ErrorNegocio(ValueError):
    codigo = 400

    def __init__(self, mensaje: str, cabeceras: Optional[dict] = None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.cabeceras = cabeceras


class Invalido(ErrorNegocio):
    """Datos que incumplen una regla de validación (400)."""
    codigo = 400


class NoAutenticado(ErrorNegocio):
    """Sesión ausente, inválida, vencida o cerrada (401)."""
    codigo = 401


class SinPermiso(ErrorNegocio):
    """El usuario autenticado no puede hacer la operación (403)."""
    codigo = 403


class NoEncontrado(ErrorNegocio):
    """El recurso indicado no existe (404)."""
    codigo = 404


class Conflicto(ErrorNegocio):
    """El estado actual impide la operación: duplicados o reglas de estado (409)."""
    codigo = 409


class TipoContenido(ErrorNegocio):
    """Content-Type no soportado (415)."""
    codigo = 415


class DemasiadosIntentos(ErrorNegocio):
    """Bloqueo temporal por intentos fallidos; se acompaña del encabezado Retry-After (429)."""
    codigo = 429


class NoDisponible(ErrorNegocio):
    """Falla de almacenamiento (503)."""
    codigo = 503


# ── Clase global ─────────────────────────────────────────────────────────────
class GlobalException:

    @staticmethod
    def respuesta(mensaje: str, codigo: int, cabeceras: Optional[dict] = None) -> JSONResponse:
        """Respuesta de error con el formato { mensaje, data, success }."""
        return JSONResponse(status_code=codigo, content={"mensaje": mensaje, "data": None, "success": False},
                            headers=cabeceras)

    # -- se usan en las rutas ---------------------------------------------------
    @staticmethod
    def mensajes(por_campo: dict):
        """Decorador de una ruta: mensaje propio de la HU cuando falla un campo concreto."""
        def _marcar(funcion):
            funcion.mensajes_validacion = por_campo
            return funcion
        return _marcar

    @staticmethod
    async def exigir_json(request: Request):
        """Dependencia: si la petición trae cuerpo, el Content-Type debe ser application/json (415)."""
        if request.method in ("POST", "PUT", "PATCH"):
            cuerpo = await request.body()
            if cuerpo and not request.headers.get("content-type", "").lower().startswith("application/json"):
                raise TipoContenido(MSG_CONTENT_TYPE)

    @staticmethod
    def simular_falla(mensaje_503: str):
        """Dependencia: permite probar en Swagger el 503 y el 500 con el campo X-Simular-Falla = bd | error."""
        async def _dependencia(x_simular_falla: Optional[str] = Header(
                None, alias="X-Simular-Falla",
                description="Solo para pruebas: escriba bd (503) o error (500). Déjelo vacío en el uso normal.")):
            falla = (x_simular_falla or "").lower()
            if falla == "bd":
                raise NoDisponible(mensaje_503)
            if falla == "error":
                raise RuntimeError("Falla no controlada simulada")
        return _dependencia

    # -- traducción de los errores de validación de Pydantic --------------------
    @staticmethod
    def _mensaje_validacion(errores: list, por_campo: dict) -> str:
        err = errores[0]
        tipo, loc = err.get("type", ""), tuple(err.get("loc", ()))
        campo = loc[1] if len(loc) > 1 and loc[0] == "body" else None
        if campo in por_campo and tipo not in ("extra_forbidden", "string_too_long"):
            return por_campo[campo]
        if loc and loc[0] == "path":
            return MSG_ID
        if tipo in ("json_invalid", "model_attributes_type") or (tipo == "missing" and loc == ("body",)):
            return MSG_JSON
        if tipo == "value_error":
            return str(err["ctx"]["error"])
        if tipo == "missing":
            return MSG_OBLIGATORIOS
        if tipo == "extra_forbidden":
            return MSG_EXTRA
        if tipo in ("string_too_long", "too_long"):
            return MSG_LARGO
        return MSG_TIPO

    # -- registro en la aplicación (se llama una sola vez en main.py) -----------
    @classmethod
    def registrar(cls, app: FastAPI) -> None:
        @app.exception_handler(ErrorNegocio)
        async def _negocio(_: Request, exc: ErrorNegocio):
            return cls.respuesta(exc.mensaje, exc.codigo, exc.cabeceras)

        @app.exception_handler(RequestValidationError)
        async def _validacion(request: Request, exc: RequestValidationError):
            por_campo = getattr(request.scope.get("endpoint"), "mensajes_validacion", {})
            return cls.respuesta(cls._mensaje_validacion(exc.errors(), por_campo), 400)

        @app.exception_handler(StarletteHTTPException)
        async def _http(_: Request, exc: StarletteHTTPException):
            if exc.status_code == 404:
                return cls.respuesta("El recurso solicitado no existe", 404)
            if exc.status_code == 405:
                return cls.respuesta("El método HTTP no está permitido para este recurso", 405)
            return cls.respuesta(str(exc.detail), exc.status_code)

        @app.exception_handler(Exception)
        async def _inesperado(_: Request, exc: Exception):
            return cls.respuesta(MSG_500, 500)

        # Swagger: quitar el 422 automático de FastAPI (esta API responde 400 en validación)
        abrir_openapi = app.openapi

        def _openapi_sin_422():
            esquema = abrir_openapi()
            for ruta in esquema.get("paths", {}).values():
                for operacion in ruta.values():
                    operacion.get("responses", {}).pop("422", None)
            esquema.get("components", {}).get("schemas", {}).pop("HTTPValidationError", None)
            esquema.get("components", {}).get("schemas", {}).pop("ValidationError", None)
            return esquema

        app.openapi = _openapi_sin_422
