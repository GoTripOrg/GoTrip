"""Servicio de roles y permisos: orquesta dominio + repositorio. No conoce HTTP ni FastAPI."""
from domain.rol_domain import PERMISO_ROLES_CONSULTAR
from domain.usuario_domain import Usuario
from global_exception import NoEncontrado, SinPermiso
from repository.rol_repository import RolRepository

MSG_EXITO = "Consulta de roles exitosa"
MSG_SIN_PERMISO = "No tiene permiso para consultar roles y permisos"
MSG_NO_EXISTE = "El rol indicado no existe"


class RolService:
    def __init__(self, repo: RolRepository):
        self.repo = repo

    def tiene_permiso(self, usuario: Usuario, codigo: str) -> bool:
        """Permisos de todos los roles de la cuenta: roles internos y modos de uso."""
        nombres = list(usuario.roles_internos) + [m.capitalize() for m in usuario.modos_habilitados]
        roles = [self.repo.obtener_por_nombre(n) for n in nombres]
        return any(r is not None and r.tiene_permiso(codigo) for r in roles)

    def verificar_permiso_consulta(self, usuario: Usuario) -> None:
        if not self.tiene_permiso(usuario, PERMISO_ROLES_CONSULTAR):
            raise SinPermiso(MSG_SIN_PERMISO)

    def consultar(self) -> list[dict]:
        """HU-026: los siete roles con sus permisos fijos (solo lectura)."""
        return [r.to_response() for r in sorted(self.repo.obtener_todos(), key=lambda r: r.id_rol)]

    def obtener(self, id_rol: int) -> dict:
        rol = self.repo.obtener_por_id(id_rol)
        if rol is None:
            raise NoEncontrado(MSG_NO_EXISTE)
        return rol.to_response()
