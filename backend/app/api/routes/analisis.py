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
    user=Depends(get_current_user)
):
    usuario_id = user.get("sub")
    contenido_id = None

    # 🔥 VALIDACIÓN INTELIGENTE
    if tipo == "texto" and not texto:
        raise HTTPException(status_code=400, detail="Debe proporcionar el texto a analizar.")
    
    elif tipo == "url" and not url:
        raise HTTPException(status_code=400, detail="Debe proporcionar una URL válida.")
    
    elif tipo in ["imagen", "video"] and not archivo and not url:
        raise HTTPException(status_code=400, detail="Debe subir un archivo o proporcionar el enlace multimedia.")

    try:
        contenido_id = repo.guardar_contenido(
            tipo=tipo,
            texto=texto,
            url=url,
            usuario_id=usuario_id
        )

        imagen_bytes = None
        if archivo:
            imagen_bytes = await archivo.read()

        texto_a_analizar = texto if texto else url

        analisis_ia = ia_service.analizar_contenido(
            texto=texto_a_analizar,
            imagen_bytes=imagen_bytes
        )

        repo.actualizar_estado(
            contenido_id=contenido_id,
            nuevo_estado="completado"
        )

        return {
            "mensaje": "Análisis completado",
            "contenido_id": contenido_id,
            "resultado": analisis_ia.get("resultado"),
            "score_credibilidad": analisis_ia.get("score_credibilidad"),
            "detalles": analisis_ia.get("detalles"),
            "recomendacion": analisis_ia.get("recomendacion"),
            "fuentes": analisis_ia.get("fuentes", [])
        }

    except Exception as e:
        error_msg = str(e).lower()
        print(f"🚨 ERROR INTERNO DEL SERVIDOR: {error_msg}")

        if contenido_id:
            try:
                repo.actualizar_estado(
                    contenido_id=contenido_id,
                    nuevo_estado="error"
                )
            except Exception as db_error:
                print(f"🚨 ERROR AL ACTUALIZAR ESTADO: {str(db_error)}")

        # 🔥 NUEVO: Interceptor de Límites de Google (Error 429)
        if "429" in error_msg or "quota" in error_msg or "exhausted" in error_msg:
            raise HTTPException(
                status_code=429,
                detail="El sistema está procesando un alto volumen de información. Por favor, espera 60 segundos antes de analizar otro contenido."
            )

        # Error general para cualquier otro fallo
        raise HTTPException(
            status_code=500,
            detail="Tuvimos un problema interno al procesar tu solicitud. Intenta nuevamente."
        )