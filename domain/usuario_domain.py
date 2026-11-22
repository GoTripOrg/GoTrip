"""Dominio: cuenta de usuario (HU-022). Sin FastAPI ni acceso a datos.
UsuarioCreate = entrada, UsuarioResponse = salida, Usuario = entidad con sus reglas."""
import re
from datetime import datetime, timedelta, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr, field_validator

from global_exception import MSG_OBLIGATORIOS, MSG_TIPO

MSG_MODO = "El modo de uso no es válido. Escoja viajero o proveedor"
MSG_CORREO = "El correo electrónico no tiene un formato válido"
MSG_CLAVE = "La contraseña no cumple la política de seguridad"
MSG_ACEPTA = "Debe aceptar el tratamiento de datos personales para registrarse"
MODOS_USO = ("viajero", "proveedor")
ZONA = timezone(timedelta(hours=-5))  # hora de Colombia


def ahora() -> datetime:
    return datetime.now(ZONA).replace(tzinfo=None, microsecond=0)


def iso(valor: Optional[datetime]) -> Optional[str]:
    """ISO 8601 con desfase, p. ej. 2026-11-12T19:30:00-05:00."""
    return None if valor is None else valor.replace(tzinfo=ZONA).isoformat()


MAX_BYTES_CONTRASENA = 72  # límite de bcrypt para generar el hash


def politica_contrasena(c: str) -> bool:
    """Valor inicial propuesto: mínimo 8 caracteres, con mayúscula, minúscula y número,
    y como máximo 72 bytes (lo que admite bcrypt)."""
    return (8 <= len(c) and len(c.encode()) <= MAX_BYTES_CONTRASENA
            and any(x.isupper() for x in c) and any(x.islower() for x in c) and any(x.isdigit() for x in c))


class UsuarioCreate(BaseModel):
    """Cuerpo de POST /api/v1/usuarios/registro."""
    model_config = ConfigDict(extra="forbid")

    modo_uso: StrictStr = Field(..., description="`viajero` o `proveedor`")
    nombres: StrictStr = Field(..., max_length=100)
    apellidos: StrictStr = Field(..., max_length=100)
    correo: StrictStr = Field(..., max_length=150)
    id_tipo_documento: StrictInt = Field(..., description="Debe existir en el catálogo (HU-006)")
    numero_documento: StrictStr = Field(..., max_length=30)
    telefono: StrictStr = Field(..., max_length=20, description="Solo dígitos, con indicativo opcional")
    contrasena: StrictStr = Field(..., max_length=128, description="Mínimo 8 caracteres, con mayúscula, minúscula y número")
    acepta_tratamiento_datos: StrictBool = Field(..., description="Debe ser `true`")

    @field_validator("modo_uso")
    @classmethod
    def _modo(cls, v):
        if v not in MODOS_USO:
            raise ValueError(MSG_MODO)
        return v

    @field_validator("nombres", "apellidos", "numero_documento", "telefono", "contrasena")
    @classmethod
    def _no_vacio(cls, v):
        if not v.strip():
            raise ValueError(MSG_OBLIGATORIOS)
        return v

    @field_validator("nombres", "apellidos")
    @classmethod
    def _limpiar(cls, v):
        return v.strip()

    @field_validator("correo")
    @classmethod
    def _correo(cls, v):
        v = v.strip().lower()
        if not v:
            raise ValueError(MSG_OBLIGATORIOS)
        if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]{2,}", v) is None:
            raise ValueError(MSG_CORREO)
        return v

    @field_validator("telefono")
    @classmethod
    def _telefono(cls, v):
        if re.fullmatch(r"\+?[0-9]{7,15}", v.strip()) is None:
            raise ValueError(MSG_TIPO)  # la HU no define mensaje propio para el teléfono
        return v.strip()

    @field_validator("contrasena")
    @classmethod
    def _clave(cls, v):
        if not politica_contrasena(v):
            raise ValueError(MSG_CLAVE)
        return v

    @field_validator("acepta_tratamiento_datos")
    @classmethod
    def _acepta(cls, v):
        if v is not True:
            raise ValueError(MSG_ACEPTA)
        return v


class UsuarioResponse(BaseModel):
    """Datos que devuelve la API (nunca la contraseña)."""
    id_usuario: int
    nombres: str
    apellidos: str
    correo: str
    modo_uso: str
    estado: str
    fecha_creacion: str


class RespuestaRegistro(BaseModel):
    """Envoltorio de la respuesta exitosa de HU-022."""
    mensaje: str
    data: UsuarioResponse
    success: bool


class Usuario:
    def __init__(self, id_usuario: int, nombres: str, apellidos: str, correo: str, id_tipo_documento: int,
                 numero_documento: str, telefono: str, hash_contrasena: str, modo_uso: str,
                 fecha_creacion: datetime, estado: str = "activo"):
        self.id_usuario = id_usuario
        self.nombres = nombres
        self.apellidos = apellidos
        self.correo = correo
        self.id_tipo_documento = id_tipo_documento
        self.numero_documento = numero_documento
        self.telefono = telefono
        self.hash_contrasena = hash_contrasena
        self.modo_uso = modo_uso
        self.modos_habilitados = [modo_uso]
        self.estado = estado
        self.fecha_creacion = fecha_creacion

    def esta_activo(self) -> bool:
        """RN-02: solo una cuenta activa puede autenticarse."""
        return self.estado == "activo"

    def to_response(self) -> dict:
        return {"id_usuario": self.id_usuario, "nombres": self.nombres, "apellidos": self.apellidos,
                "correo": self.correo, "modo_uso": self.modo_uso, "estado": self.estado,
                "fecha_creacion": iso(self.fecha_creacion)}
