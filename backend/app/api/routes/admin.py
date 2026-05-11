import os

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
from app.infrastructure.repositories.analisis_repo import AnalisisRepository
from app.infrastructure.auth_handler import get_current_user

router = APIRouter(prefix="/api/admin", tags=["Admin"])

analisis_repo = AnalisisRepository()
load_dotenv()

API_CATALOG = [
    {
        "id": "gemini",
        "nombre": "Gemini",
        "proveedor": "Google AI",
        "variable_env": "GEMINI_API_KEY",
        "uso": "Analisis de texto e imagenes",
        "test_implementado": True,
    },
    {
        "id": "google_fact_check",
        "nombre": "Google Fact Check Tools",
        "proveedor": "Google",
        "variable_env": "GOOGLE_FACT_CHECK_API_KEY",
        "uso": "Consulta de verificaciones externas",
        "test_implementado": False,
    },
    {
        "id": "news_api",
        "nombre": "News API",
        "proveedor": "NewsAPI.org",
        "variable_env": "NEWS_API_KEY",
        "uso": "Busqueda de noticias recientes",
        "test_implementado": False,
    },
    {
        "id": "youtube_data",
        "nombre": "YouTube Data API",
        "proveedor": "Google",
        "variable_env": "YOUTUBE_API_KEY",
        "uso": "Analisis futuro de enlaces y videos",
        "test_implementado": False,
    },
]


def _api_status(api: dict) -> dict:
    configurada = bool(os.getenv(api["variable_env"]))
    if not configurada:
        estado = "sin_configurar"
    elif api["test_implementado"]:
        estado = "activa"
    else:
        estado = "no_implementada"

    return {
        "id": api["id"],
        "nombre": api["nombre"],
        "proveedor": api["proveedor"],
        "estado": estado,
        "configurada": configurada,
        "variable_env": api["variable_env"],
        "uso": api["uso"],
        "test_implementado": api["test_implementado"],
    }

@router.get("/metricas")
def obtener_metricas(user=Depends(get_current_user)):
    """Retorna métricas generales del dashboard de administrador."""
    try:
        return analisis_repo.obtener_metricas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/apis")
def obtener_apis(user=Depends(get_current_user)):
    """Retorna el catalogo de APIs externas sin exponer claves privadas."""
    return {"apis": [_api_status(api) for api in API_CATALOG]}


@router.post("/apis/{api_id}/test")
def probar_api(api_id: str, user=Depends(get_current_user)):
    """Prueba una API externa cuando el conector ya existe en el proyecto."""
    api = next((item for item in API_CATALOG if item["id"] == api_id), None)
    if not api:
        raise HTTPException(status_code=404, detail="API no encontrada.")

    status = _api_status(api)
    if not status["configurada"]:
        return {
            "success": False,
            "estado": "sin_configurar",
            "mensaje": f"Falta configurar {status['variable_env']} en el backend.",
        }

    if api_id != "gemini":
        return {
            "success": False,
            "estado": "no_implementada",
            "mensaje": "La API esta registrada para uso futuro, pero aun no tiene prueba de conexion.",
        }

    try:
        import google.generativeai as genai

        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content("Responde unicamente con la palabra OK.")
        if not getattr(response, "text", "").strip():
            raise Exception("Gemini no devolvio una respuesta valida.")

        return {
            "success": True,
            "estado": "activa",
            "mensaje": "Conexion verificada.",
        }
    except Exception as e:
        return {
            "success": False,
            "estado": "error",
            "mensaje": f"No se pudo verificar la conexion: {str(e)}",
        }
