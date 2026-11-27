"""Repositorio en memoria de roles y permisos (catálogo fijo; datos semilla). Sin reglas de negocio."""
from typing import Optional

from domain.rol_domain import (PERMISO_PARAMETROS_CONSULTAR, PERMISO_ROLES_CONSULTAR,
                               PERMISO_USUARIOS_ASIGNAR_ROL, Rol)


class RolRepository:
    def __init__(self):
        self._datos: list = []
        self._seed()

    def _seed(self):
        """Los 7 roles fijos. Permisos propuestos; los demás se agregan con las HU que los usan."""
        self._datos = [
            Rol(1, "Viajero", False, []),
            Rol(2, "Proveedor", False, []),
            Rol(3, "Administrador", True, [PERMISO_USUARIOS_ASIGNAR_ROL, PERMISO_ROLES_CONSULTAR,
                                           PERMISO_PARAMETROS_CONSULTAR]),
            Rol(4, "Gestor de soporte", True, [PERMISO_PARAMETROS_CONSULTAR]),
            Rol(5, "Verificador legal", True, []),
            Rol(6, "Aprobador de liquidaciones", True, []),
            Rol(7, "Moderador de reseñas", True, []),
        ]

    def obtener_todos(self) -> list:
        return list(self._datos)

    def obtener_por_nombre(self, nombre: str) -> Optional[Rol]:
        return next((r for r in self._datos if r.nombre.lower() == nombre.lower()), None)


rol_repository = RolRepository()
