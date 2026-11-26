# ─────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA — crea la app FastAPI y registra los routers
# ─────────────────────────────────────────────────────────────
import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI  # noqa: E402

from global_exception import GlobalException  # noqa: E402
from api.auth_api import router as auth_router  # noqa: E402
from api.tipo_documento_api import router as tipo_documento_router  # noqa: E402
from api.usuario_api import router as usuario_router, router_administrador  # noqa: E402

app = FastAPI(
    title="GoTrip – Servicios web (MVP)",
    description="API REST con arquitectura de capas (api, service, domain, repository). "
                "Datos en memoria con datos de prueba; las respuestas siguen el contrato "
                "{ mensaje, data, success } documentado en cada historia de usuario.",
    version="1.0.0",
)
GlobalException.registrar(app)

# Registrar los routers de cada entidad (los de las demás HU se agregan aquí al construirse)
app.include_router(tipo_documento_router, prefix="/api/v1")
app.include_router(usuario_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(router_administrador, prefix="/api/v1")


# Ruta raíz — bienvenida
@app.get("/", tags=["Sistema"])
def root():
    return {"mensaje": "API corriendo correctamente 🚀", "docs": "http://127.0.0.1:8000/docs", "version": "1.0.0"}


@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok", "version": "1.0.0", "environment": os.getenv("APP_ENV", "development")}


# ── Para correr directamente con: python main.py ─────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
