from fastapi import APIRouter, HTTPException, Form, File, UploadFile, Depends, Request
from typing import Optional
import hashlib # 🔥 IMPORTAMOS HASHLIB PARA LOS DUPLICADOS

from app.infrastructure.repositories.contenido_repo import ContenidoRepository
from app.infrastructure.ai.gemini_service import GeminiService
from app.infrastructure.auth_handler import get_current_user
import requests
from bs4 import BeautifulSoup

router = APIRouter(prefix="/api/analisis", tags=["Analisis"])

repo = ContenidoRepository()
ia_service = GeminiService()

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

    # Capturamos IP y Dispositivo
    ip_usuario = request.client.host if request.client else None
    dispositivo = request.headers.get("user-agent")

    # Validaciones
    if tipo == "texto" and not texto:
        raise HTTPException(status_code=400, detail="Debe proporcionar el texto a analizar.")
    elif tipo == "url" and not url:
        raise HTTPException(status_code=400, detail="Debe proporcionar una URL válida.")
    elif tipo in ["imagen", "video"] and not archivo and not url:
        raise HTTPException(status_code=400, detail="Debe subir un archivo o proporcionar el enlace multimedia.")

    try:
        imagen_bytes = None
        hash_archivo = None

        # 🔥 LÓGICA ANTI-DUPLICADOS (Caché con Hash)
        if archivo:
            imagen_bytes = await archivo.read()
            # Creamos la huella digital de la imagen (SHA-256)
            hash_archivo = hashlib.sha256(imagen_bytes).hexdigest()
            
            # Consultamos si ya existe
            resultado_previo = repo.buscar_por_hash(hash_archivo)
            
            if resultado_previo:
                # Si ya existe, devolvemos los datos directo de la BD (Cero llamadas a Gemini)
                return {
                    "mensaje": "Análisis recuperado de la base de datos (Caché).",
                    "resultado": "Real" if resultado_previo[2] == "verificado" else "Fake",
                    "estado": resultado_previo[2],
                    "score_credibilidad": float(resultado_previo[0]),
                    "nivel_credibilidad": resultado_previo[1],
                    "detalles": "Esta imagen ya fue verificada previamente por el sistema.",
                    "recomendacion": "Revisa las fuentes proporcionadas en el análisis original.",
                    "fuentes": [], # Opcional: podrías guardar las fuentes en la BD también
                    "ahorro_tokens": True
                }

        # Si no existe en BD, procedemos a guardar (Estado: en_proceso)
        contenido_id = repo.guardar_contenido(
            tipo=tipo,
            texto=texto,
            url=url,
            usuario_id=usuario_id,
            ip_usuario=ip_usuario, 
            dispositivo=dispositivo,
            hash_archivo=hash_archivo # <-- Guardamos el hash
        )

        texto_a_analizar = texto if texto else url

        # Llamamos a Gemini
        analisis_ia = ia_service.analizar_contenido(
            texto=texto_a_analizar,
            imagen_bytes=imagen_bytes
        )

        # Lógica de cierre sin NULLs
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

        return {
            "mensaje": "Análisis completado",
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
        print(f"🚨 ERROR INTERNO DEL SERVIDOR: {error_msg}")

        if contenido_id:
            try:
                repo.actualizar_estado(contenido_id=contenido_id, nuevo_estado="error")
            except Exception as db_error:
                print(f" ERROR AL ACTUALIZAR ESTADO: {str(db_error)}")

        if "429" in error_msg or "quota" in error_msg or "exhausted" in error_msg:
            raise HTTPException(
                status_code=429,
                detail="El sistema está procesando un alto volumen de información. Por favor, espera."
            )

        raise HTTPException(
            status_code=500,
            detail="Tuvimos un problema interno al procesar tu solicitud. Intenta nuevamente."
        )