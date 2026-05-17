from fastapi import APIRouter, HTTPException, Form, File, UploadFile, Depends, Request
from typing import Optional
import hashlib

from app.infrastructure.repositories.contenido_repo import ContenidoRepository
from app.infrastructure.ai.gemini_service import GeminiService
from app.infrastructure.ai.gemini_video_service import GeminiVideoService 
from app.infrastructure.utils.video_downloader import descargar_video
from app.infrastructure.auth_handler import get_current_user

router = APIRouter(prefix="/api/analisis", tags=["Analisis"])

repo = ContenidoRepository()
ia_service = GeminiService()
ia_video_service = GeminiVideoService()

@router.post("/")
async def procesar_contenido(
    request: Request,
    tipo: str = Form(...),
    texto: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
    archivo: Optional[UploadFile] = File(None),
    user=Depends(get_current_user)
):
    usuario_id = user.get("sub")
    contenido_id = None

    ip_usuario = request.client.host if request.client else None
    dispositivo = request.headers.get("user-agent")

    if tipo == "texto" and not texto:
        raise HTTPException(status_code=400, detail="Debe proporcionar el texto a analizar.")
    elif tipo == "url" and not url:
        raise HTTPException(status_code=400, detail="Debe proporcionar una URL válida.")
    elif tipo in ["imagen", "video"] and not archivo and not url:
        raise HTTPException(status_code=400, detail="Debe subir un archivo o proporcionar el enlace multimedia.")

    try:
        imagen_bytes = None
        hash_archivo = None

        if archivo:
            imagen_bytes = await archivo.read()
            hash_archivo = hashlib.sha256(imagen_bytes).hexdigest()
            
            resultado_previo = repo.buscar_por_hash(hash_archivo)
            if resultado_previo:
                return {
                    "mensaje": "Análisis recuperado de la base de datos (Caché).",
                    "resultado": "Real" if resultado_previo[2] == "verificado" else "Fake",
                    "estado": resultado_previo[2],
                    "score_credibilidad": float(resultado_previo[0]),
                    "nivel_credibilidad": resultado_previo[1],
                    "detalles": "Esta información ya fue verificada previamente para optimizar recursos.",
                    "ahorro_tokens": True
                }

        contenido_id = repo.guardar_contenido(
            tipo=tipo,
            texto=texto,
            url=url,
            usuario_id=usuario_id,
            ip_usuario=ip_usuario, 
            dispositivo=dispositivo,
            hash_archivo=hash_archivo
        )

        texto_a_analizar = texto if texto else url
        analisis_ia = None

        if tipo == "video":
            if archivo:
                mime_type = archivo.content_type if archivo.content_type else "video/mp4"
                analisis_ia = ia_video_service.analizar_video(
                    video_bytes=imagen_bytes, 
                    mime_type=mime_type
                )
            elif url:
                try:
                    video_descargado_bytes = descargar_video(url)
                    analisis_ia = ia_video_service.analizar_video(
                        video_bytes=video_descargado_bytes,
                        mime_type="video/mp4"
                    )
                except Exception as e:
                    raise Exception(f"Error al procesar URL de video: {str(e)}")
        else:
            analisis_ia = ia_service.analizar_contenido(
                texto=texto_a_analizar,
                imagen_bytes=imagen_bytes
            )

        score = analisis_ia.get("score_credibilidad", 0)
        nivel = analisis_ia.get("nivel_credibilidad", "baja")
        resultado_texto = analisis_ia.get("resultado", "Fake")

        estado_final = "verificado" if resultado_texto.lower() == "real" else "desmentido"

        repo.finalizar_verificacion(
            contenido_id=contenido_id,
            score=score,
            nivel=nivel,
            estado_final=estado_final
        )

        # 🔥 NUEVO: GUARDAR LA JUSTIFICACIÓN DE LA IA EN LA BD
        repo.guardar_retroalimentacion(
            contenido_id=contenido_id,
            detalles=analisis_ia.get("detalles", "Análisis completado sin detalles específicos."),
            recomendacion=analisis_ia.get("recomendacion", ""),
            fuentes=analisis_ia.get("fuentes", []),
            modelo_ia="gemini-2.5-flash"
        )

        return {
            "mensaje": "Análisis completado exitosamente",
            "contenido_id": contenido_id,
            "resultado": resultado_texto,
            "estado": estado_final,
            "score_credibilidad": score,
            "nivel_credibilidad": nivel,
            "detalles": analisis_ia.get("detalles"),
            "recomendacion": analisis_ia.get("recomendacion"),
            "fuentes": analisis_ia.get("fuentes", [])
        }

    except Exception as e:
        error_msg = str(e).lower()
        print(f"Error en el flujo de análisis: {error_msg}")

        if contenido_id:
            try:
                repo.actualizar_estado(contenido_id=contenido_id, nuevo_estado="error")
            except Exception as db_error:
                print(f"Error al marcar estado de error en BD: {str(db_error)}")

        if "429" in error_msg or "quota" in error_msg:
            raise HTTPException(
                status_code=429,
                detail="Se ha alcanzado el límite de peticiones. Por favor, intente en un minuto."
            )

        raise HTTPException(
            status_code=500,
            detail="Error interno al procesar el análisis. Intente nuevamente."
        )


@router.get("/historial")
async def obtener_historial(user=Depends(get_current_user)):
    try:
        usuario_id = user.get("sub")
        historial_db = repo.obtener_historial_por_usuario(usuario_id)
        
        historial_formateado = []
        for h in historial_db:
            historial_formateado.append({
                "type": h.get("tipo", "texto"),
                "date": h.get("fecha").strftime("%d/%m/%Y, %H:%M:%S") if h.get("fecha") else "Sin fecha",
                "result": "Real 🟢" if h.get("estado") == "verificado" else "Fake ❌",
                "confidence": h.get("confidence") or 0,
                "details": h.get("details") or "Sin detalles adicionales.",
                "recomendacion": h.get("recomendacion") or "",
                "fuentes": h.get("fuentes") or []
            })
            
        return historial_formateado

    except Exception as e:
        print(f"🚨 ERROR EN ENDPOINT /historial: {str(e)}")
        raise HTTPException(status_code=500, detail="No se pudo obtener el historial.")