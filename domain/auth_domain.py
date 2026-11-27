"""Dominio: inicio de sesión (HU-023). Sin FastAPI ni acceso a datos.
LoginRequest = entrada, RespuestaLogin = salida, ControlIntentos = reglas del bloqueo temporal."""
from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator

from domain.usuario_domain import MODOS_USO, MSG_MODO

MSG_CREDENCIALES_FALTAN = "Debe ingresar el correo y la contraseña"
MINUTOS_BLOQUEO = (5, 15, 30, 60)  # bloqueos sucesivos; el de 60 minutos se mantiene para los siguientes


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    correo: StrictStr = Field(..., min_length=1, max_length=254)
    contrasena: StrictStr = Field(..., min_length=1, max_length=128)
    modo_uso: Optional[StrictStr] = Field(
        None, description="viajero o proveedor; opcional solo para cuentas con rol interno")

    @field_validator("correo")
    @classmethod
    def _correo(cls, v: str) -> str:
        v = v.strip().lower()
        if not v:
            raise ValueError(MSG_CREDENCIALES_FALTAN)
        return v

    @field_validator("modo_uso")
    @classmethod
    def _modo(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip().lower()
        if v not in MODOS_USO:
            raise ValueError(MSG_MODO)
        return v


class UsuarioSesion(BaseModel):
    id_usuario: int
    nombres: str
    modo_activo: Optional[str]
    modos_disponibles: list[str]
    roles_internos: list[str]


class DatosSesion(BaseModel):
    token_acceso: str
    tipo_token: str
    expira_en: int
    usuario: UsuarioSesion


class RespuestaLogin(BaseModel):
    """Envoltorio de la respuesta exitosa de HU-023."""
    mensaje: str
    data: DatosSesion
    success: bool


class ControlIntentos:
    """Intentos fallidos consecutivos y bloqueo temporal de un correo (exista o no la cuenta).
    El bloqueo no es un estado de la cuenta: termina solo al vencer su tiempo."""

    def __init__(self, correo: str):
        self.correo = correo
        self.fallos = 0
        self.bloqueos = 0
        self.bloqueado_hasta: Optional[datetime] = None

    def segundos_bloqueo(self, momento: datetime) -> int:
        """Segundos que faltan del bloqueo vigente (0 si no hay bloqueo)."""
        if self.bloqueado_hasta is None or momento >= self.bloqueado_hasta:
            return 0
        return max(1, int((self.bloqueado_hasta - momento).total_seconds() + 0.999))

    def registrar_fallo(self, momento: datetime, maximo: int) -> None:
        self.fallos += 1
        if self.fallos >= maximo:
            minutos = MINUTOS_BLOQUEO[min(self.bloqueos, len(MINUTOS_BLOQUEO) - 1)]
            self.bloqueado_hasta = momento + timedelta(minutes=minutos)
            self.bloqueos += 1
            self.fallos = 0

    def registrar_exito(self) -> None:
        """Reinicia el contador de fallos; el número de bloqueos se conserva para que el siguiente sea más largo."""
        self.fallos = 0
        self.bloqueado_hasta = None


class RespuestaLogout(BaseModel):
    """Envoltorio de la respuesta exitosa de HU-024 (`data` siempre es null)."""
    mensaje: str
    data: None = None
    success: bool
