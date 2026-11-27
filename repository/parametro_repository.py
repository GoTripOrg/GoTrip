"""Repositorio en memoria de parámetros globales (datos semilla de HU-018). Sin reglas de negocio."""
from domain.parametro_domain import Parametro


class ParametroRepository:
    def __init__(self):
        self._datos: list = []
        self._seed()

    def _seed(self):
        """Valores propuestos (Observaciones de HU-018). No hay parámetros de notificaciones todavía.
        La comisión de la plataforma queda pendiente: no tiene valor definido."""
        self._datos = [
            Parametro("TIEMPO_LIBERACION_CUPO_MIN", "Tiempo de liberación de cupo bloqueado", "int", 15,
                      "reservas", "operacion"),
            Parametro("IVA_PORCENTAJE", "Porcentaje de IVA vigente", "double", 19.0, "pagos", "operacion"),
            Parametro("DURACION_TOKEN_SEG", "Duración del token de acceso (segundos)", "int", 86400,
                      "autenticacion", "seguridad"),
            Parametro("MAX_INTENTOS_LOGIN", "Máximo de intentos fallidos de inicio de sesión", "int", 3,
                      "autenticacion", "seguridad"),
            Parametro("BLOQUEOS_LOGIN_MIN", "Duración de los bloqueos sucesivos de inicio de sesión (minutos)",
                      "string", "5,15,30,60", "autenticacion", "seguridad"),
            Parametro("VIGENCIA_CODIGO_RECUPERACION_MIN", "Vigencia del código de recuperación (minutos)", "int",
                      15, "recuperacion_contrasena", "seguridad"),
            Parametro("MAX_SOLICITUDES_RECUPERACION_DIA", "Máximo de solicitudes de recuperación por correo al día",
                      "int", 3, "recuperacion_contrasena", "seguridad"),
            Parametro("CONTRASENA_LONGITUD_MINIMA", "Longitud mínima de la contraseña (caracteres)", "int", 8,
                      "contrasenas", "seguridad"),
            Parametro("CONTRASENA_MAX_BYTES", "Tamaño máximo de la contraseña (bytes)", "int", 72,
                      "contrasenas", "seguridad"),
        ]

    def obtener_todos(self) -> list:
        return list(self._datos)

    def obtener_por_categoria(self, categoria: str) -> list:
        return [p for p in self._datos if p.categoria == categoria]


parametro_repository = ParametroRepository()
