"""Repositorio en memoria de autenticación: intentos de inicio de sesión, control de bloqueos y sesiones."""
import threading
from datetime import datetime
from typing import Optional

from domain.auth_domain import ControlIntentos


class AuthRepository:
    def __init__(self):
        self._lock = threading.Lock()
        self.reiniciar()

    def reiniciar(self):
        self._intentos: list = []     # registro de cada intento (nunca guarda la contraseña)
        self._controles: dict = {}    # correo -> ControlIntentos
        self._sesiones: dict = {}     # jti -> datos de la sesión (HU-024 la invalidará)

    def control(self, correo: str) -> ControlIntentos:
        with self._lock:
            return self._controles.setdefault(correo, ControlIntentos(correo))

    def registrar_intento(self, correo: str, fecha: datetime, exitoso: bool, motivo: str,
                          id_usuario: Optional[int] = None) -> None:
        with self._lock:
            self._intentos.append({"correo": correo, "fecha": fecha, "exitoso": exitoso,
                                   "motivo": motivo, "id_usuario": id_usuario})

    def obtener_intentos(self, correo: Optional[str] = None) -> list:
        return [i for i in self._intentos if correo is None or i["correo"] == correo]

    def registrar_sesion(self, jti: str, id_usuario: int, modo_activo: Optional[str], vence: datetime) -> None:
        with self._lock:
            self._sesiones[jti] = {"id_usuario": id_usuario, "modo_activo": modo_activo, "vence": vence,
                                   "activa": True}

    def obtener_sesion(self, jti: str) -> Optional[dict]:
        return self._sesiones.get(jti)


auth_repository = AuthRepository()
