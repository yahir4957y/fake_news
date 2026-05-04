import google.generativeai as genai
import os
import json
import io
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def analizar_contenido(self, texto: str = None, imagen_bytes: bytes = None):
        prompt = """
        Eres un investigador periodístico experto y fact-checker profesional. 
        Analiza el contenido proporcionado. Si es una imagen, extrae el texto (OCR), describe el contexto visual y evalúa si parece manipulada.
        Si es texto o URL, analiza la semántica buscando evidencia comprobable. 
        MUY IMPORTANTE: NO asumas que algo es "Fake" solo porque suena sensacionalista, inusual o político. Verifica si relata hechos reportados por medios reales o eventos verificables. Si los hechos o declaraciones sucedieron en la realidad, clasifícalo como "Real". Solo clasifica como "Fake" si hay evidencia clara de falsedad, manipulación de hechos, afirmaciones pseudocientíficas desmentidas, o si proviene de sitios de sátira/engaño conocidos.
        
        Proporciona contexto útil para que el usuario entienda de dónde proviene o de qué trata.
        Sugiere fuentes confiables (ej. enlaces a búsquedas de Google News o artículos relacionados) para que el usuario verifique por sí mismo.
        
        Responde ÚNICA Y EXCLUSIVAMENTE con un objeto JSON válido con esta estructura exacta, sin texto adicional:
        {
            "resultado": "Real" o "Fake",
            "score_credibilidad": un número entero del 0 al 100,
            "detalles": "Explicación clara, intuitiva y directa (máximo 3 líneas) de por qué es real o fake, escrita para que cualquier persona la entienda fácilmente",
            "contexto": "Datos de fondo relevantes o explicación del evento para que el usuario entienda mejor la noticia",
            "fuentes_confiables": [
                {
                    "nombre": "Búsqueda en Google News u otro medio oficial",
                    "url": "https://news.google.com/search?q=palabras+clave+de+la+noticia"
                }
            ],
            "recomendacion": "Qué debería hacer el usuario con esta info"
        }
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