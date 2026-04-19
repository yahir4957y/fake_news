from fastapi import APIRouter, HTTPException, Form, File, UploadFile, Depends
from typing import Optional
from app.infrastructure.repositories.contenido_repo import ContenidoRepository
from app.infrastructure.ai.gemini_service import GeminiService
from app.infrastructure.auth_handler import get_current_user

router = APIRouter(prefix="/api/analisis", tags=["Analisis"])
repo = ContenidoRepository()
ia_service = GeminiService()

@router.post("/")
async def procesar_contenido(
    tipo: str = Form(...),
    texto: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
    archivo: Optional[UploadFile] = File(None),
    user = Depends(get_current_user) 
):
    try:
        
        contenido_id = repo.guardar_contenido(tipo=tipo, texto=texto, url=url)

      
        imagen_bytes = None
        if archivo:
            imagen_bytes = await archivo.read()

        
        texto_a_analizar = texto if texto else url
        analisis_ia = ia_service.analizar_contenido(
            texto=texto_a_analizar, 
            imagen_bytes=imagen_bytes
        )

        return {
            "mensaje": "Análisis completado",
            "contenido_id": contenido_id,
            "resultado": analisis_ia.get("resultado"),
            "score_credibilidad": analisis_ia.get("score_credibilidad"),
            "detalles": analisis_ia.get("detalles"),
            "recomendacion": analisis_ia.get("recomendacion")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))