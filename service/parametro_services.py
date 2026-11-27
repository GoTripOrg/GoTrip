"""Servicio de parámetros globales: orquesta dominio + repositorios. No conoce HTTP ni FastAPI."""
from typing import Optional

from domain.parametro_domain import CATEGORIAS, MSG_CATEGORIA
from domain.rol_domain import PERMISO_PARAMETROS_CONSULTAR
from domain.usuario_domain import Usuario
from global_exception import Invalido, SinPermiso
from repository.parametro_repository import ParametroRepository
from repository.rol_repository import RolRepository

MSG_EXITO = "Consulta de parámetros globales exitosa"
MSG_VACIO = "No hay parámetros para la categoría indicada"
MSG_SIN_PERMISO = "No tiene permiso para consultar los parámetros globales"


class ParametroService:
    def __init__(self, repo: ParametroRepository, repo_roles: RolRepository):
        self.repo = repo
        self.repo_roles = repo_roles

    def _tiene_permiso(self, usuario: Usuario, permiso: str) -> bool:
        """Permisos de todos los roles de la cuenta: roles internos y modos de uso."""
        nombres = list(usuario.roles_internos) + [m.capitalize() for m in usuario.modos_habilitados]
        roles = [self.repo_roles.obtener_por_nombre(n) for n in nombres]
        return any(r is not None and r.tiene_permiso(permiso) for r in roles)

    def consultar(self, usuario: Usuario, categoria: Optional[str]) -> tuple[str, list[dict]]:
        """HU-018: parámetros vigentes, con filtro opcional por categoría (RN-18: solo lectura)."""
        if not self._tiene_permiso(usuario, PERMISO_PARAMETROS_CONSULTAR):
            raise SinPermiso(MSG_SIN_PERMISO)
        if categoria is None:
            parametros = self.repo.obtener_todos()
        else:
            categoria = categoria.strip().lower()
            if categoria not in CATEGORIAS:
                raise Invalido(MSG_CATEGORIA)
            parametros = self.repo.obtener_por_categoria(categoria)
        if not parametros:
            return MSG_VACIO, []
        return MSG_EXITO, [p.to_response() for p in parametros]
