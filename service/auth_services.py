"""Servicio de autenticación: orquesta dominio + repositorios. No conoce HTTP ni FastAPI."""
from domain.auth_domain import LoginRequest
from domain.usuario_domain import MSG_MODO, ahora
from global_exception import DemasiadosIntentos, Invalido, NoAutenticado, SinPermiso
from repository.auth_repository import AuthRepository
from repository.usuario_repository import UsuarioRepository
from service.seguridad import DURACION_TOKEN_SEG, MAX_INTENTOS_LOGIN, crear_token, verificar_contrasena

MSG_EXITO = "Inicio de sesión exitoso"
MSG_CREDENCIALES = "Correo o contraseña incorrectos"
MSG_BLOQUEO = ("Demasiados intentos fallidos. El inicio de sesión está bloqueado temporalmente; "
               "intente de nuevo más tarde")
MSG_INACTIVA = "La cuenta está inactiva y no puede iniciar sesión"
MSG_MODO_NO_ACTIVO = "El modo de uso elegido no está activado en su cuenta"


class AuthService:
    def __init__(self, repo_usuarios: UsuarioRepository, repo_auth: AuthRepository):
        self.repo_usuarios = repo_usuarios
        self.repo_auth = repo_auth

    def iniciar_sesion(self, datos: LoginRequest) -> dict:
        """HU-023: valida credenciales, estado (RN-02) y modo; entrega el token de acceso."""
        momento = ahora()
        control = self.repo_auth.control(datos.correo)

        espera = control.segundos_bloqueo(momento)
        if espera:
            self.repo_auth.registrar_intento(datos.correo, momento, False, "bloqueado")
            raise DemasiadosIntentos(MSG_BLOQUEO, {"Retry-After": str(espera)})

        usuario = self.repo_usuarios.obtener_por_correo(datos.correo)
        hash_guardado = usuario.hash_contrasena if usuario else None
        if not verificar_contrasena(datos.contrasena, hash_guardado):
            control.registrar_fallo(momento, MAX_INTENTOS_LOGIN)
            self.repo_auth.registrar_intento(datos.correo, momento, False, "credenciales",
                                             usuario.id_usuario if usuario else None)
            raise NoAutenticado(MSG_CREDENCIALES)  # mismo mensaje exista o no el correo

        if not usuario.esta_activo():  # RN-02
            self.repo_auth.registrar_intento(datos.correo, momento, False, "inactiva", usuario.id_usuario)
            raise SinPermiso(MSG_INACTIVA)

        # El modo se revisa después de la contraseña para no revelar qué correos existen
        if datos.modo_uso is None:
            if not usuario.tiene_rol_interno():
                self.repo_auth.registrar_intento(datos.correo, momento, False, "sin_modo", usuario.id_usuario)
                raise Invalido(MSG_MODO)
        elif datos.modo_uso not in usuario.modos_habilitados:
            self.repo_auth.registrar_intento(datos.correo, momento, False, "modo_no_activo", usuario.id_usuario)
            raise SinPermiso(MSG_MODO_NO_ACTIVO)

        control.registrar_exito()
        token, jti, vence = crear_token(usuario.id_usuario, datos.modo_uso, usuario.roles_internos)
        self.repo_auth.registrar_sesion(jti, usuario.id_usuario, datos.modo_uso, vence)
        self.repo_auth.registrar_intento(datos.correo, momento, True, "exitoso", usuario.id_usuario)
        return {
            "token_acceso": token,
            "tipo_token": "Bearer",
            "expira_en": DURACION_TOKEN_SEG,
            "usuario": {
                "id_usuario": usuario.id_usuario,
                "nombres": usuario.nombres,
                "modo_activo": datos.modo_uso,
                "modos_disponibles": list(usuario.modos_habilitados),
                "roles_internos": list(usuario.roles_internos),
            },
        }
