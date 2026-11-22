"""Seguridad compartida: verificación de contraseñas (bcrypt) y tokens de acceso (JWT con jti)."""
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt

# Parámetros de seguridad (valores del script semilla: DURACION_TOKEN_SEG y MAX_INTENTOS_LOGIN)
DURACION_TOKEN_SEG = 86400
MAX_INTENTOS_LOGIN = 3
ALGORITMO = "HS256"

# Hash de referencia para que un correo inexistente tarde lo mismo que uno existente
_HASH_REFERENCIA = bcrypt.hashpw(b"referencia", bcrypt.gensalt()).decode()

# bcrypt solo admite hasta 72 bytes; una contraseña más larga nunca coincide con un hash guardado
MAX_BYTES_BCRYPT = 72


def verificar_contrasena(contrasena: str, hash_guardado: Optional[str]) -> bool:
    """Compara la contraseña con su hash. Si no hay hash o la contraseña supera los 72 bytes,
    igual hace el cálculo (mismo tiempo de respuesta) y devuelve False."""
    clave = contrasena.encode()
    if len(clave) > MAX_BYTES_BCRYPT:
        bcrypt.checkpw(b"referencia", _HASH_REFERENCIA.encode())
        return False
    coincide = bcrypt.checkpw(clave, (hash_guardado or _HASH_REFERENCIA).encode())
    return coincide and hash_guardado is not None


def _clave() -> str:
    clave = os.getenv("SECRET_KEY")
    if not clave:
        raise RuntimeError("Falta SECRET_KEY en el archivo .env")
    return clave


def crear_token(id_usuario: int, modo_activo: Optional[str], roles_internos: list) -> tuple:
    """Token de acceso de 24 h. Devuelve (token, jti, vencimiento)."""
    emitido = datetime.now(timezone.utc)
    vence = emitido + timedelta(seconds=DURACION_TOKEN_SEG)
    jti = uuid.uuid4().hex
    datos = {"sub": str(id_usuario), "jti": jti, "iat": emitido, "exp": vence,
             "modo": modo_activo, "roles": roles_internos}
    return jwt.encode(datos, _clave(), algorithm=ALGORITMO), jti, vence
