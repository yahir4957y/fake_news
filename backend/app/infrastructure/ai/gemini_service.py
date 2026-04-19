import google.generativeai as genai
import os
import json
import io
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("AIzaSyBsCufoYLFXMQEbf5hmFRgQDb0wlYKghqk"))

class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def analizar_contenido(self, texto: str = None, imagen_bytes: bytes = None):
        prompt = """
        Eres un experto analista de ciberseguridad y fact-checking. 
        Analiza el contenido proporcionado. Si es una imagen, extrae el texto (OCR), describe el contexto visual y evalúa si parece manipulada.
        Si es texto o URL, analiza la semántica buscando patrones de desinformación, clickbait o fuentes falsas.
        
        Responde ÚNICA Y EXCLUSIVAMENTE con un objeto JSON válido con esta estructura exacta, sin texto adicional:
        {
            "resultado": "Real" o "Fake",
            "score_credibilidad": un número entero del 0 al 100,
            "detalles": "Breve explicación de por qué es real o fake",
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