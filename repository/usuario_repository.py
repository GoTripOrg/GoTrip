"""Repositorio en memoria de usuarios. Solo guarda y recupera datos; sin reglas de negocio."""
import threading
from datetime import datetime
from typing import Optional

from domain.usuario_domain import Usuario

# Hash bcrypt de la contraseña de prueba "Clave1234" (datos semilla, no son datos reales)
HASH_CLAVE_PRUEBA = "$2b$12$dMXb3M13DzX4MpOfVijFFuEXt3hTm1veMeCGAVMIscyRXj5SFctKK"


class UsuarioRepository:
    def __init__(self):
        self._lock = threading.Lock()
        self.reiniciar()

    def reiniciar(self):
        """Vuelve al estado inicial: solo los datos semilla."""
        self._datos: list = []
        self._siguiente_id = 1
        self._seed()

    def _seed(self):
        """Cuentas de prueba (HU-023): una inactiva y una con solo rol interno.
        Usan ids altos para no cambiar los ids de las cuentas que se registran en las pruebas (1, 2, ...)."""
        fecha = datetime(2026, 11, 1, 8, 0, 0)
        self._datos += [
            Usuario(90, "Inés", "Rincón", "inactivo@correo.com", 1, "52111222", "3005556677", HASH_CLAVE_PRUEBA,
                    "viajero", fecha, estado="inactivo"),
            Usuario(91, "Sofía", "Pardo", "soporte@gotrip.co", 1, "52333444", "3008889900", HASH_CLAVE_PRUEBA,
                    None, fecha, roles_internos=["Gestor de soporte"]),
        ]

    def obtener_todos(self) -> list:
        return list(self._datos)

    def obtener_por_id(self, id_usuario: int) -> Optional[Usuario]:
        return next((u for u in self._datos if u.id_usuario == id_usuario), None)

    def obtener_por_correo(self, correo: str) -> Optional[Usuario]:
        return next((u for u in self._datos if u.correo == correo.lower()), None)

    def obtener_por_documento(self, id_tipo_documento: int, numero: str) -> Optional[Usuario]:
        return next((u for u in self._datos
                     if u.id_tipo_documento == id_tipo_documento and u.numero_documento == numero), None)

    def crear(self, **campos) -> Usuario:
        with self._lock:
            nuevo = Usuario(id_usuario=self._siguiente_id, **campos)
            self._datos.append(nuevo)
            self._siguiente_id += 1
            return nuevo


usuario_repository = UsuarioRepository()
