"""Dominio: roles y permisos (catálogo fijo cargado con el script semilla). Sin FastAPI ni acceso a datos.
Viajero y Proveedor son modos de uso; los otros cinco roles son internos y los asigna el Administrador."""

PERMISO_PARAMETROS_CONSULTAR = "PARAMETROS_CONSULTAR"
PERMISO_ROLES_CONSULTAR = "ROLES_CONSULTAR"
PERMISO_USUARIOS_ASIGNAR_ROL = "USUARIOS_ASIGNAR_ROL"


class Rol:
    def __init__(self, id_rol: int, nombre: str, interno: bool, permisos: list):
        self.id_rol = id_rol
        self.nombre = nombre
        self.interno = interno  # False = modo de uso (Viajero, Proveedor)
        self.permisos = list(permisos)

    def tiene_permiso(self, permiso: str) -> bool:
        return permiso in self.permisos
