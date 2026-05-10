import uuid as uuid_lib
import hashlib

from fastapi import APIRouter, HTTPException, Form, File, UploadFile, Depends, Request
from typing import Optional

from app.infrastructure.repositories.contenido_repo import ContenidoRepository
from app.infrastructure.ai.gemini_service import GeminiService
from app.infrastructure.auth_handler import get_current_user
from app.application.services.token_service import TokenService

import requests
from bs4 import BeautifulSoup

# ══════════════════════════════════════════════════════════════════════════════
# CAMBIOS RESPECTO A LA VERSIÓN ORIGINAL:
#   1. Se importa uuid_lib para generar UUIDs desde el Clerk sub
#   2. Se convierte el Clerk sub (ej. "user_2abc") a UUID con uuid5
#   3. Se llama a repo.upsert_usuario() para sincronizar el usuario en la BD
#   4. guardar_contenido() ahora recibe el UUID en vez del sub de Clerk
#   5. Se llama a repo.guardar_verificacion() con el resultado de Gemini
#   6. Se llama a repo.guardar_retroalimentacion() con detalles y fuentes
#   7. Se llama a repo.guardar_historial() para registrar la consulta
#   8. El response ahora incluye verificacion_id (útil para el historial, paso 3)
#   9. La lógica de tokens fue separada a token_service.py
#   10. Se agregó sistema anti-duplicados con hash SHA-256
# ══════════════════════════════════════════════════════════════════════════════

router = APIRouter(prefix="/api/analisis", tags=["Analisis"])

repo = ContenidoRepository()
ia_service = GeminiService()
token_service = TokenService()


@router.post("/")
async def procesar_contenido(
    request: Request,
    tipo: str = Form(...),
    texto: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
    archivo: Optional[UploadFile] = File(None),
    user=Depends(get_current_user)
):

    # ── ORIGINAL ──────────────────────────────────────────────────────────────
    # ORIGINAL: usuario_id = user.get("sub")  → string tipo "user_2abc123"
    # NUEVO: convertimos ese string a UUID determinístico con uuid5.
    # uuid5 + NAMESPACE_URL garantiza que el mismo sub siempre da el mismo UUID,
    # lo que permite hacer UPSERT sin duplicar al usuario en la tabla usuarios.
    clerk_sub = user.get("sub")
    usuario_uuid = str(uuid_lib.uuid5(uuid_lib.NAMESPACE_URL, clerk_sub))

    # ── NUEVO: sincronizar usuario de Clerk con la tabla usuarios ─────────────
    # El JWT de Clerk puede traer email/nombre si están configurados en Clerk Dashboard.
    # Si no los trae, upsert_usuario usa un placeholder para no violar el NOT NULL.
    repo.upsert_usuario(
        usuario_uuid=usuario_uuid,
        email=user.get("email"),
        nombre=user.get("name") or user.get("given_name"),
        foto_url=user.get("image_url")
    )

    contenido_id = None
    verificacion_id = None

    # Capturamos IP y Dispositivo
    ip_usuario = request.client.host if request.client else None
    dispositivo = request.headers.get("user-agent")

    # ── ORIGINAL: validación de entrada ───────────────────────────────────────
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
                    "fuentes": [],
                    "ahorro_tokens": True
                }

        # ── ORIGINAL: guarda el contenido ──────────────────────────────────────
        contenido_id = repo.guardar_contenido(
            tipo=tipo,
            texto=texto,
            url=url,
            usuario_id=usuario_uuid,
            ip_usuario=ip_usuario,
            dispositivo=dispositivo,
            hash_archivo=hash_archivo
        )

        texto_a_analizar = texto if texto else url

        # ── ORIGINAL: llamar a Gemini ─────────────────────────────────────────
        analisis_ia = ia_service.analizar_contenido(
            texto=texto_a_analizar,
            imagen_bytes=imagen_bytes
        )

        # ── NUEVO: registrar consumo de tokens en servicio separado ──────────
        token_service.registrar_consumo(
            analisis_ia,
            usuario_uuid,
            user
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

        # ── NUEVO: persistir el veredicto en verificaciones ───────────────────
        verificacion_id = repo.guardar_verificacion(
            contenido_id=contenido_id,
            usuario_id=usuario_uuid,
            resultado=analisis_ia.get("resultado"),
            score=analisis_ia.get("score_credibilidad")
        )

        # ── NUEVO: persistir el feedback completo de Gemini ───────────────────
        repo.guardar_retroalimentacion(
            verificacion_id=verificacion_id,
            resumen=analisis_ia.get("detalles"),
            recomendacion=analisis_ia.get("recomendacion"),
            fuentes=analisis_ia.get("fuentes", [])
        )

        # ── NUEVO: registrar en historial_consultas ───────────────────────────
        repo.guardar_historial(usuario_id=usuario_uuid, contenido_id=contenido_id)

        # ── ORIGINAL + NUEVO: response incluye verificacion_id ───────────────
        return {
            "mensaje": "Análisis completado",
            "contenido_id": contenido_id,
            "verificacion_id": verificacion_id,
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

        # ── ORIGINAL: marcar como error si el contenido ya fue guardado ───────
        if contenido_id:
            try:
                repo.actualizar_estado(contenido_id=contenido_id, nuevo_estado="error")
            except Exception as db_error:
                print(f"🚨 ERROR AL ACTUALIZAR ESTADO: {str(db_error)}")

        # ── ORIGINAL: interceptor de límite de cuota de Google (Error 429) ────
        if "429" in error_msg or "quota" in error_msg or "exhausted" in error_msg:
            raise HTTPException(
                status_code=429,
                detail="El sistema está procesando un alto volumen de información. Por favor, espera 60 segundos antes de analizar otro contenido."
            )

        # ── ORIGINAL: error genérico ──────────────────────────────────────────
        raise HTTPException(
            status_code=500,
            detail="Tuvimos un problema interno al procesar tu solicitud. Intenta nuevamente."
        )


# ── NUEVO (PASO 3): endpoint para recuperar el historial desde la BD ──────────
# GET /api/analisis/historial  →  devuelve los últimos 50 análisis del usuario.
# El frontend lo llama al cargar el dashboard y cuando regresa a la aplicación,
# reemplazando el localStorage que antes era la única fuente de historial.
@router.get("/historial")
def obtener_historial(user=Depends(get_current_user)):
    clerk_sub = user.get("sub")
    usuario_uuid = str(uuid_lib.uuid5(uuid_lib.NAMESPACE_URL, clerk_sub))

    try:
        historial = repo.obtener_historial(usuario_uuid)
        return {"historial": historial}
    except Exception as e:
        print(f"Error al obtener historial: {str(e)}")
        raise HTTPException(status_code=500, detail="No se pudo recuperar el historial.")