"""Repositorio en memoria de usuarios. Solo guarda y recupera datos; sin reglas de negocio."""
import threading
from typing import Optional

from domain.usuario_domain import Usuario


class UsuarioRepository:
    def __init__(self):
        self._lock = threading.Lock()
        self.reiniciar()

    def reiniciar(self):
        """Vacía el almacén (lo usan las pruebas)."""
        self._datos: list = []
        self._siguiente_id = 1

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
