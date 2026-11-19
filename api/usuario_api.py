"""Capa API: rutas de usuarios. Solo recibe la petición, llama al servicio y devuelve la respuesta.
Los errores los atiende GlobalException (carpeta global_exception)."""
from fastapi import APIRouter, Body, Depends

from domain.usuario_domain import MSG_MODO, RespuestaRegistro, UsuarioCreate
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
