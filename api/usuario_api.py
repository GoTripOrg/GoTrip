"""Capa API: rutas de usuarios. Solo recibe la petición, llama al servicio y devuelve la respuesta.
Los errores los atiende GlobalException (carpeta global_exception)."""
from fastapi import APIRouter, Body, Depends

from domain.usuario_domain import (MSG_MODO, AdministradorInicialCreate, RespuestaAdministrador, RespuestaRegistro,
                                 UsuarioCreate)
from global_exception import GlobalException
from repository.tipo_documento_repository import tipo_documento_repository
from repository.usuario_repository import usuario_repository
from service.usuario_services import UsuarioService

router = APIRouter(prefix="/usuarios", tags=["MOD-04 · Usuarios y acceso"])
service = UsuarioService(repo=usuario_repository, repo_tipos=tipo_documento_repository)

MSG_503 = "No fue posible registrar la cuenta. Intente de nuevo más tarde"

# Un ejemplo por cada caso de prueba del documento HU-022 (desplegable «Examples» de Swagger)
EJEMPLOS = {
    "caso_01": {
        "summary": "Caso 1 · Registro exitoso como viajero (HTTP 201)",
        "description": "Esperado: HTTP 201 · «Cuenta registrada correctamente».",
        "value": {
            "modo_uso": "viajero",
            "nombres": "Laura",
            "apellidos": "Rojas",
            "correo": "laura@correo.com",
            "id_tipo_documento": 1,
            "numero_documento": "1098765432",
            "telefono": "3001234567",
            "contrasena": "Clave1234",
            "acepta_tratamiento_datos": True
        }
    },
    "caso_02": {
        "summary": "Caso 2 · Registro exitoso como proveedor (HTTP 201)",
        "description": "Esperado: HTTP 201 · «Cuenta registrada correctamente».",
        "value": {
            "modo_uso": "proveedor",
            "nombres": "Carlos",
            "apellidos": "Mejía",
            "correo": "carlos.mejia@correo.com",
            "id_tipo_documento": 1,
            "numero_documento": "79123456",
            "telefono": "3109876543",
            "contrasena": "Clave1234",
            "acepta_tratamiento_datos": True
        }
    },
    "caso_03": {
        "summary": "Caso 3 · Correo repetido (HTTP 409)",
        "description": "Esperado: HTTP 409 · «El correo electrónico ya está registrado». Ejecute antes el caso 1.",
        "value": {
            "modo_uso": "viajero",
            "nombres": "Laura",
            "apellidos": "Rojas",
            "correo": "laura@correo.com",
            "id_tipo_documento": 1,
            "numero_documento": "52000111",
            "telefono": "3001234567",
            "contrasena": "Clave1234",
            "acepta_tratamiento_datos": True
        }
    },
    "caso_04": {
        "summary": "Caso 4 · Documento repetido (HTTP 409)",
        "description": "Esperado: HTTP 409 · «El número de documento ya está registrado». Ejecute antes el caso 1.",
        "value": {
            "modo_uso": "viajero",
            "nombres": "Laura",
            "apellidos": "Rojas",
            "correo": "otra.laura@correo.com",
            "id_tipo_documento": 1,
            "numero_documento": "1098765432",
            "telefono": "3001234567",
            "contrasena": "Clave1234",
            "acepta_tratamiento_datos": True
        }
    },
    "caso_05": {
        "summary": "Caso 5 · Campos obligatorios faltantes (HTTP 400)",
        "description": "Esperado: HTTP 400 · «Hay campos obligatorios sin diligenciar».",
        "value": {
            "modo_uso": "viajero",
            "nombres": "Laura",
            "correo": "laura@correo.com",
            "id_tipo_documento": 1,
            "numero_documento": "1098765432",
            "telefono": "3001234567",
            "contrasena": "Clave1234",
            "acepta_tratamiento_datos": True
        }
    },
    "caso_06": {
        "summary": "Caso 6 · Modo de uso inválido (HTTP 400)",
        "description": "Esperado: HTTP 400 · «El modo de uso no es válido. Escoja viajero o proveedor».",
        "value": {
            "modo_uso": "admin",
            "nombres": "Laura",
            "apellidos": "Rojas",
            "correo": "laura@correo.com",
            "id_tipo_documento": 1,
            "numero_documento": "1098765432",
            "telefono": "3001234567",
            "contrasena": "Clave1234",
            "acepta_tratamiento_datos": True
        }
    },
    "caso_07": {
        "summary": "Caso 7 · Correo con formato inválido (HTTP 400)",
        "description": "Esperado: HTTP 400 · «El correo electrónico no tiene un formato válido».",
        "value": {
            "modo_uso": "viajero",
            "nombres": "Laura",
            "apellidos": "Rojas",
            "correo": "laura.com",
            "id_tipo_documento": 1,
            "numero_documento": "1098765432",
            "telefono": "3001234567",
            "contrasena": "Clave1234",
            "acepta_tratamiento_datos": True
        }
    },
    "caso_08": {
        "summary": "Caso 8 · Documento con formato inválido (HTTP 400)",
        "description": "Esperado: HTTP 400 · «El número de documento no cumple el formato del tipo de documento».",
        "value": {
            "modo_uso": "viajero",
            "nombres": "Laura",
            "apellidos": "Rojas",
            "correo": "laura@correo.com",
            "id_tipo_documento": 1,
            "numero_documento": "12345678901",
            "telefono": "3001234567",
            "contrasena": "Clave1234",
            "acepta_tratamiento_datos": True
        }
    },
    "caso_09": {
        "summary": "Caso 9 · Contraseña débil (HTTP 400)",
        "description": "Esperado: HTTP 400 · «La contraseña no cumple la política de seguridad».",
        "value": {
            "modo_uso": "viajero",
            "nombres": "Laura",
            "apellidos": "Rojas",
            "correo": "laura@correo.com",
            "id_tipo_documento": 1,
            "numero_documento": "1098765432",
            "telefono": "3001234567",
            "contrasena": "12345",
            "acepta_tratamiento_datos": True
        }
    },
    "caso_10": {
        "summary": "Caso 10 · No acepta el tratamiento de datos (HTTP 400)",
        "description": "Esperado: HTTP 400 · «Debe aceptar el tratamiento de datos personales para registrarse».",
        "value": {
            "modo_uso": "viajero",
            "nombres": "Laura",
            "apellidos": "Rojas",
            "correo": "laura@correo.com",
            "id_tipo_documento": 1,
            "numero_documento": "1098765432",
            "telefono": "3001234567",
            "contrasena": "Clave1234",
            "acepta_tratamiento_datos": False
        }
    },
    "caso_11": {
        "summary": "Caso 11 · Tipo de documento inexistente (HTTP 404)",
        "description": "Esperado: HTTP 404 · «El tipo de documento indicado no existe».",
        "value": {
            "modo_uso": "viajero",
            "nombres": "Laura",
            "apellidos": "Rojas",
            "correo": "laura@correo.com",
            "id_tipo_documento": 9999,
            "numero_documento": "1098765432",
            "telefono": "3001234567",
            "contrasena": "Clave1234",
            "acepta_tratamiento_datos": True
        }
    },
    "caso_12": {
        "summary": "Caso 12 · Falla de base de datos (HTTP 503)",
        "description": "Esperado: HTTP 503 · «No fue posible registrar la cuenta. Intente de nuevo más tarde». Escriba en el campo X-Simular-Falla el valor «bd».",
        "value": {
            "modo_uso": "viajero",
            "nombres": "Laura",
            "apellidos": "Rojas",
            "correo": "prueba.bd@correo.com",
            "id_tipo_documento": 1,
            "numero_documento": "30111222",
            "telefono": "3001234567",
            "contrasena": "Clave1234",
            "acepta_tratamiento_datos": True
        }
    },
    "caso_15": {
        "summary": "Caso 15 · Campo con tipo de dato incorrecto (HTTP 400)",
        "description": "Esperado: HTTP 400 · «Uno de los campos tiene un tipo de dato incorrecto».",
        "value": {
            "modo_uso": "viajero",
            "nombres": "Laura",
            "apellidos": "Rojas",
            "correo": "laura@correo.com",
            "id_tipo_documento": "abc",
            "numero_documento": "1098765432",
            "telefono": "3001234567",
            "contrasena": "Clave1234",
            "acepta_tratamiento_datos": True
        }
    },
    "caso_16": {
        "summary": "Caso 16 · Campos no permitidos en el cuerpo (HTTP 400)",
        "description": "Esperado: HTTP 400 · «La petición contiene campos no permitidos».",
        "value": {
            "modo_uso": "viajero",
            "nombres": "Laura",
            "apellidos": "Rojas",
            "correo": "laura@correo.com",
            "id_tipo_documento": 1,
            "numero_documento": "1098765432",
            "telefono": "3001234567",
            "contrasena": "Clave1234",
            "acepta_tratamiento_datos": True,
            "rol": "administrador",
            "estado": "activo"
        }
    },
    "caso_17": {
        "summary": "Caso 17 · Campo que supera la longitud máxima (HTTP 400)",
        "description": "Esperado: HTTP 400 · «Uno de los campos supera la longitud máxima permitida».",
        "value": {
            "modo_uso": "viajero",
            "nombres": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "apellidos": "Rojas",
            "correo": "laura@correo.com",
            "id_tipo_documento": 1,
            "numero_documento": "1098765432",
            "telefono": "3001234567",
            "contrasena": "Clave1234",
            "acepta_tratamiento_datos": True
        }
    },
    "caso_18": {
        "summary": "Caso 18 · Error inesperado del servidor (HTTP 500)",
        "description": "Esperado: HTTP 500 · «Ocurrió un error inesperado. Intente de nuevo más tarde». Escriba en el campo X-Simular-Falla el valor «error».",
        "value": {
            "modo_uso": "viajero",
            "nombres": "Laura",
            "apellidos": "Rojas",
            "correo": "prueba.error@correo.com",
            "id_tipo_documento": 1,
            "numero_documento": "30333444",
            "telefono": "3001234567",
            "contrasena": "Clave1234",
            "acepta_tratamiento_datos": True
        }
    }
}


@router.post(
    "/registro", status_code=201, response_model=RespuestaRegistro, summary="HU-022 · Registrar cuenta de usuario",
    dependencies=[Depends(GlobalException.exigir_json), Depends(GlobalException.simular_falla(MSG_503))],
)
@GlobalException.mensajes({"modo_uso": MSG_MODO})
def registrar_usuario(datos: UsuarioCreate = Body(..., openapi_examples=EJEMPLOS)):
    """Crea la cuenta en estado **activo** con el modo de uso elegido (viajero o proveedor).
    El correo y el documento no pueden repetirse (RN-01). La contraseña se guarda solo como hash."""
    return RespuestaRegistro(mensaje="Cuenta registrada correctamente", data=service.registrar(datos), success=True)


# ── HU-165 · Registrar la cuenta administradora inicial ──────────────────────
router_administrador = APIRouter(prefix="/administrador-inicial", tags=["MOD-04 · Usuarios y acceso"])

MSG_503_ADMIN = "No fue posible registrar la cuenta administradora. Intente de nuevo más tarde"


def registro_inicial_disponible():
    """Dependencia: si ya hay un Administrador responde 409 antes de procesar los datos."""
    service.verificar_registro_inicial_disponible()


def _ejemplo(summary: str, description: str, value: dict) -> dict:
    return {"summary": summary, "description": description, "value": value}


ADMIN = {
    "nombres": "Ana María",
    "apellidos": "Gómez Pérez",
    "correo": "admin@gotrip.co",
    "id_tipo_documento": 1,
    "numero_documento": "1012345678",
    "telefono": "3151234567",
    "contrasena": "Admin1234"
}
SIN_CORREO = {k: v for k, v in ADMIN.items() if k != "correo"}

# Un ejemplo por cada caso de prueba del documento HU-165 (desplegable «Examples» de Swagger).
# Se ejecutan primero los casos 4 a 16 y al final los casos 1, 2 y 3. El caso 2 se ejecuta en POST /api/v1/auth/login.
EJEMPLOS_ADMIN = {
    "caso_01": _ejemplo("Caso 1 · Registro exitoso de la primera cuenta administradora (HTTP 201)",
                        "Esperado: HTTP 201 · «Cuenta administradora inicial registrada correctamente». "
                        "Ejecútelo después de los casos 4 a 16.", ADMIN),
    "caso_03": _ejemplo("Caso 3 · Segundo intento de registro inicial (HTTP 409)",
                        "Esperado: HTTP 409 · «Ya existe una cuenta administradora; el registro inicial no está "
                        "disponible». Ejecute antes el caso 1.",
                        {"nombres": "Pedro", "apellidos": "Salazar Ruiz", "correo": "segundo.admin@gotrip.co",
                         "id_tipo_documento": 1, "numero_documento": "1012345679", "telefono": "3157654321",
                         "contrasena": "Admin1234"}),
    "caso_04": _ejemplo("Caso 4 · Campos obligatorios sin diligenciar (HTTP 400)",
                        "Esperado: HTTP 400 · «Hay campos obligatorios sin diligenciar».", SIN_CORREO),
    "caso_05": _ejemplo("Caso 5 · Correo con formato inválido (HTTP 400)",
                        "Esperado: HTTP 400 · «El correo electrónico no tiene un formato válido».",
                        {**ADMIN, "correo": "admin.gotrip"}),
    "caso_06": _ejemplo("Caso 6 · Número de documento con formato inválido (HTTP 400)",
                        "Esperado: HTTP 400 · «El número de documento no cumple el formato del tipo de documento».",
                        {**ADMIN, "numero_documento": "12345678901"}),
    "caso_07": _ejemplo("Caso 7 · Contraseña que no cumple la política (HTTP 400)",
                        "Esperado: HTTP 400 · «La contraseña no cumple la política de seguridad».",
                        {**ADMIN, "contrasena": "abc123"}),
    "caso_08": _ejemplo("Caso 8 · Tipo de documento inexistente (HTTP 404)",
                        "Esperado: HTTP 404 · «El tipo de documento indicado no existe».",
                        {**ADMIN, "id_tipo_documento": 9999}),
    "caso_09": _ejemplo("Caso 9 · Correo o documento ya registrados (HTTP 409)",
                        "Esperado: HTTP 409 · «El correo o el número de documento ya están registrados». "
                        "Usa el correo de la cuenta semilla soporte@gotrip.co.",
                        {**ADMIN, "correo": "soporte@gotrip.co"}),
    "caso_10": _ejemplo("Caso 10 · Falla de base de datos (HTTP 503)",
                        "Esperado: HTTP 503 · «No fue posible registrar la cuenta administradora. Intente de nuevo "
                        "más tarde». Escriba en el campo X-Simular-Falla el valor «bd».", ADMIN),
    "caso_13": _ejemplo("Caso 13 · Campo con tipo de dato incorrecto (HTTP 400)",
                        "Esperado: HTTP 400 · «Uno de los campos tiene un tipo de dato incorrecto».",
                        {**ADMIN, "id_tipo_documento": "abc"}),
    "caso_14": _ejemplo("Caso 14 · Campos no permitidos en el cuerpo (HTTP 400)",
                        "Esperado: HTTP 400 · «La petición contiene campos no permitidos».",
                        {**ADMIN, "rol": "Viajero"}),
    "caso_15": _ejemplo("Caso 15 · Campo que supera la longitud máxima (HTTP 400)",
                        "Esperado: HTTP 400 · «Uno de los campos supera la longitud máxima permitida».",
                        {**ADMIN, "nombres": "a" * 101}),
    "caso_16": _ejemplo("Caso 16 · Error inesperado del servidor (HTTP 500)",
                        "Esperado: HTTP 500 · «Ocurrió un error inesperado. Intente de nuevo más tarde». "
                        "Escriba en el campo X-Simular-Falla el valor «error».", ADMIN),
}


@router_administrador.post(
    "", status_code=201, response_model=RespuestaAdministrador,
    summary="HU-165 · Registrar la cuenta administradora inicial",
    dependencies=[Depends(GlobalException.exigir_json), Depends(GlobalException.simular_falla(MSG_503_ADMIN)),
                  Depends(registro_inicial_disponible)],
)
def registrar_administrador_inicial(datos: AdministradorInicialCreate = Body(..., openapi_examples=EJEMPLOS_ADMIN)):
    """Crea la **única** cuenta con rol **Administrador**, en estado activo y sin modos viajero ni proveedor.
    No requiere autenticación. Si ya existe un Administrador responde 409 a cualquier intento posterior.
    El correo y el documento no pueden repetirse (RN-01). La contraseña se guarda solo como hash."""
    return RespuestaAdministrador(mensaje="Cuenta administradora inicial registrada correctamente",
                                  data=service.registrar_administrador_inicial(datos), success=True)
