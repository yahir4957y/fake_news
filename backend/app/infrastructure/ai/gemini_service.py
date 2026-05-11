import google.generativeai as genai
import os
import json
import io
import datetime 
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def analizar_contenido(self, texto: str = None, imagen_bytes: bytes = None):
        # 🔥 2. DEFINIMOS LA FECHA ACTUAL AQUÍ
        fecha_actual = datetime.datetime.now().strftime("%d de %B de %Y")
        
        # 🔥 3. CORREGIMOS EL TYPO Y USAMOS LA VARIABLE
        prompt = f"""
        Eres un experto analista de ciberseguridad y fact-checking. 
        
        🚨 CONTEXTO TEMPORAL CRÍTICO: Hoy es {fecha_actual}. 
        Cualquier noticia, periódico o evento con fecha igual o anterior a hoy es COMPLETAMENTE VÁLIDO y corresponde al pasado o presente. NO catalogues nada como falso solo por tener fecha de 2024, 2025 o 2026.
        
        Analiza el contenido y responde ÚNICA Y EXCLUSIVAMENTE con un objeto JSON válido:
        
        TAREA CRÍTICA - GENERACIÓN DE FUENTES:
        1. Identifica el "TEMA PRINCIPAL" de la noticia (ej. "Terremoto en Japón", "Nueva ley de impuestos", "Cura del cáncer"). Máximo 5 palabras.
        2. Convierte los espacios de ese tema en el símbolo "+" (ej. "Terremoto+en+Japon").
        3. Construye EXACTAMENTE estos 3 enlaces usando ese tema convertido:
           - Enlace 1 (Google Noticias): https://news.google.com/search?q=[TEMA_CON_MAS]
           - Enlace 2 (Búsqueda de desmentidos): https://www.google.com/search?q=[TEMA_CON_MAS]+verdad+o+falso+fact+check
           - Enlace 3 (Búsqueda en agencias oficiales): https://www.google.com/search?q=site:factual.afp.com+OR+site:chequeado.com+OR+site:reuters.com+[TEMA_CON_MAS]
        
        Responde ÚNICA Y EXCLUSIVAMENTE con un objeto JSON válido con esta estructura exacta:
        {{
            "resultado": "Real" o "Fake",
            "score_credibilidad": 85.5,
            "nivel_credibilidad": "alta",
            "detalles": "Explicación técnica de por qué es real o fake...",
            "recomendacion": "Recomendación para el usuario...",
            "fuentes": [
                {{
                    "nombre": "📰 Ver cobertura en Google Noticias",
                    "url": "https://news.google.com/search?q=..."
                }},
                {{
                    "nombre": "🔎 Buscar análisis de Fact-Checkers",
                    "url": "https://www.google.com/search?q=..."
                }},
                {{
                    "nombre": "🛡️ Revisar en Agencias Oficiales (AFP/Reuters)",
                    "url": "https://www.google.com/search?q=site:factual.afp.com+..."
                }}
            ]
        }}
        """
        
        contenido_a_enviar = [prompt]
        
        if texto:
            contenido_a_enviar.append(f"\nContenido de texto o URL a analizar: {texto}")
            
        if imagen_bytes:
            try:
                imagen_procesada = Image.open(io.BytesIO(imagen_bytes))
                contenido_a_enviar.append(imagen_procesada)
            except Exception as e:
                raise Exception(f"No se pudo procesar la imagen: {str(e)}")
            
        try:
            respuesta = self.model.generate_content(contenido_a_enviar)
            texto_limpio = respuesta.text.replace('```json', '').replace('```', '').strip()
            return json.loads(texto_limpio)
        except Exception as e:
            raise Exception(f"Error en la IA: {str(e)}")