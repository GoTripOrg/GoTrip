"""Dominio: roles y permisos (catálogo fijo cargado con el script semilla; HU-026). Sin FastAPI ni acceso a datos.
Viajero y Proveedor son modos de uso; los otros cinco roles son internos y los asigna el Administrador."""
from pydantic import BaseModel

PERMISO_PARAMETROS_CONSULTAR = "PARAMETROS_CONSULTAR"
PERMISO_ROLES_CONSULTAR = "ROLES_CONSULTAR"
PERMISO_USUARIOS_ASIGNAR_ROL = "USUARIOS_ASIGNAR_ROL"


class Permiso:
    def __init__(self, codigo: str, descripcion: str):
        self.codigo = codigo
        self.descripcion = descripcion

    def to_response(self) -> dict:
        return {"codigo": self.codigo, "descripcion": self.descripcion}


class Rol:
    def __init__(self, id_rol: int, nombre: str, interno: bool, permisos: list):
        self.id_rol = id_rol
        self.nombre = nombre
        self.interno = interno  # False = modo de uso (Viajero, Proveedor)
        self.permisos = list(permisos)  # lista de Permiso

    def tiene_permiso(self, codigo: str) -> bool:
        return any(p.codigo == codigo for p in self.permisos)

    def to_response(self) -> dict:
        return {"id_rol": self.id_rol, "nombre": self.nombre, "tipo": "interno" if self.interno else "modo_uso",
                "permisos": [p.to_response() for p in self.permisos]}


class PermisoResponse(BaseModel):
    codigo: str
    descripcion: str


class RolResponse(BaseModel):
    """Un rol con sus permisos fijos; `tipo` es `modo_uso` o `interno`."""
    id_rol: int
    nombre: str
    tipo: str
    permisos: list[PermisoResponse]


class RespuestaRoles(BaseModel):
    """Envoltorio de la lista de roles (HU-026)."""
    mensaje: str
    data: list[RolResponse]
    success: bool


class RespuestaRol(BaseModel):
    """Envoltorio del detalle de un rol (HU-026)."""
    mensaje: str
    data: RolResponse
    success: bool
