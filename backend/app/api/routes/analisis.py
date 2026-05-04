from fastapi import APIRouter, HTTPException, Form, File, UploadFile, Depends
from typing import Optional
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

        
        texto_a_analizar = texto
        if tipo == "url" and url:
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                title = soup.title.string if soup.title else "Sin título"
                paragraphs = soup.find_all('p')
                extracted_text = " ".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                extracted_text = extracted_text[:10000]
                
                texto_a_analizar = f"URL original: {url}\nTítulo: {title}\nContenido extraído:\n{extracted_text}"
            except Exception as e:
                print(f"Error scraping URL: {e}")
                texto_a_analizar = url
        elif not texto_a_analizar:
            texto_a_analizar = url

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
            "contexto": analisis_ia.get("contexto"),
            "fuentes_confiables": analisis_ia.get("fuentes_confiables", []),
            "recomendacion": analisis_ia.get("recomendacion")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))