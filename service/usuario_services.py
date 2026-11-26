"""Servicio de usuarios: orquesta dominio + repositorio. No conoce HTTP ni FastAPI."""
import bcrypt

from domain.usuario_domain import ROL_ADMINISTRADOR, AdministradorInicialCreate, UsuarioCreate, ahora
from global_exception import Conflicto, Invalido, NoEncontrado
from repository.tipo_documento_repository import TipoDocumentoRepository
from repository.usuario_repository import UsuarioRepository


MSG_ADMIN_EXISTE = "Ya existe una cuenta administradora; el registro inicial no está disponible"


def hash_contrasena(contrasena: str) -> str:
    """La contraseña nunca se guarda en claro: solo su hash bcrypt."""
    return bcrypt.hashpw(contrasena.encode(), bcrypt.gensalt()).decode()


class UsuarioService:
    def __init__(self, repo: UsuarioRepository, repo_tipos: TipoDocumentoRepository):
        self.repo = repo
        self.repo_tipos = repo_tipos

    def registrar(self, datos: UsuarioCreate) -> dict:
        """HU-022: crea la cuenta en estado activo con el modo elegido."""
        tipo = self.repo_tipos.obtener_por_id(datos.id_tipo_documento)
        if tipo is None:
            raise NoEncontrado("El tipo de documento indicado no existe")
        if not tipo.numero_valido(datos.numero_documento):
            raise Invalido("El número de documento no cumple el formato del tipo de documento")
        if self.repo.obtener_por_correo(datos.correo):  # RN-01
            raise Conflicto("El correo electrónico ya está registrado")
        if self.repo.obtener_por_documento(datos.id_tipo_documento, datos.numero_documento):
            raise Conflicto("El número de documento ya está registrado")
        usuario = self.repo.crear(
            nombres=datos.nombres, apellidos=datos.apellidos, correo=datos.correo,
            id_tipo_documento=datos.id_tipo_documento, numero_documento=datos.numero_documento,
            telefono=datos.telefono, hash_contrasena=hash_contrasena(datos.contrasena),
            modo_uso=datos.modo_uso, fecha_creacion=ahora())
        return usuario.to_response()

    # ── HU-165: cuenta administradora inicial ─────────────────────────────────
    def verificar_registro_inicial_disponible(self) -> None:
        """El registro inicial solo está disponible mientras no exista ningún Administrador."""
        if self.repo.existe_con_rol(ROL_ADMINISTRADOR):
            raise Conflicto(MSG_ADMIN_EXISTE)

    def registrar_administrador_inicial(self, datos: AdministradorInicialCreate) -> dict:
        """HU-165: crea la única cuenta Administrador, activa y sin modos viajero ni proveedor."""
        self.verificar_registro_inicial_disponible()
        tipo = self.repo_tipos.obtener_por_id(datos.id_tipo_documento)
        if tipo is None:
            raise NoEncontrado("El tipo de documento indicado no existe")
        if not tipo.numero_valido(datos.numero_documento):
            raise Invalido("El número de documento no cumple el formato del tipo de documento")
        if (self.repo.obtener_por_correo(datos.correo)  # RN-01
                or self.repo.obtener_por_documento(datos.id_tipo_documento, datos.numero_documento)):
            raise Conflicto("El correo o el número de documento ya están registrados")
        usuario = self.repo.crear_si_no_existe_rol(
            ROL_ADMINISTRADOR,
            nombres=datos.nombres, apellidos=datos.apellidos, correo=datos.correo,
            id_tipo_documento=datos.id_tipo_documento, numero_documento=datos.numero_documento,
            telefono=datos.telefono, hash_contrasena=hash_contrasena(datos.contrasena),
            modo_uso=None, fecha_creacion=ahora())
        if usuario is None:  # otra petición lo creó al mismo tiempo
            raise Conflicto(MSG_ADMIN_EXISTE)
        return usuario.to_response_administrador()
