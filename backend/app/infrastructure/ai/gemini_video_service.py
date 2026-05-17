import google.generativeai as genai
import time
import os
import json
import tempfile
import datetime
from dotenv import load_dotenv

load_dotenv()

class GeminiVideoService:
    def __init__(self):
        
        self.api_key = os.getenv("GEMINI_VIDEO_API_KEY")
        
    def analizar_video(self, video_bytes: bytes, mime_type: str = "video/mp4"):
        # Reconfiguramos la llave solo para esta transacción
        genai.configure(api_key=self.api_key)
        
        # Usamos el modelo optimizado para videos (flash es rápido, pro es más analítico)
        model = genai.GenerativeModel('gemini-2.5-flash')
        fecha_actual = datetime.datetime.now().strftime("%d de %B de %Y")
        
        prompt = f"""
        Eres un experto analista de ciberseguridad, fact-checking y deepfakes. 
        
        🚨 CONTEXTO TEMPORAL CRÍTICO: Hoy es {fecha_actual}. 
        Cualquier evento con fecha igual o anterior a hoy es VÁLIDO. NO catalogues nada como falso solo por tener fecha de 2024, 2025 o 2026.
        
        Analiza este video minuciosamente cuadro por cuadro. Busca inconsistencias lógicas, ediciones bruscas, marcas de agua extrañas, desincronización de audio (deepfake) o contexto engañoso.
        
        TAREA CRÍTICA - GENERACIÓN DE FUENTES:
        1. Identifica el "TEMA PRINCIPAL" del video.
        2. Convierte los espacios de ese tema en el símbolo "+".
        3. Construye EXACTAMENTE estos 3 enlaces usando ese tema convertido:
           - Enlace 1 (Google Noticias): https://news.google.com/search?q=[TEMA_CON_MAS]
           - Enlace 2 (Búsqueda de desmentidos): https://www.google.com/search?q=[TEMA_CON_MAS]+verdad+o+falso+fact+check
           - Enlace 3 (Agencias): https://www.google.com/search?q=site:factual.afp.com+OR+site:chequeado.com+OR+site:reuters.com+[TEMA_CON_MAS]
        
        Responde ÚNICA Y EXCLUSIVAMENTE con un objeto JSON válido con esta estructura exacta:
        {{
            "resultado": "Real" o "Fake",
            "score_credibilidad": 85.5,
            "nivel_credibilidad": "alta",
            "detalles": "Explicación técnica de la edición del video, audio o contexto...",
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
                    "nombre": "🛡️ Revisar en Agencias Oficiales",
                    "url": "https://www.google.com/search?q=site:factual.afp.com+..."
                }}
            ]
        }}
        """

        
        temp_video_path = ""
        try:
            # Creamos un archivo temporal que se auto-eliminará después
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
                temp_video.write(video_bytes)
                temp_video_path = temp_video.name

            print("⏳ Subiendo video a Google Gemini...")
            video_file = genai.upload_file(path=temp_video_path, mime_type=mime_type)
            

            print(f"🔄 Procesando video (Estado: {video_file.state.name})...")
            while video_file.state.name == "PROCESSING":
                print(".", end="", flush=True)
                time.sleep(3) # Pausamos 3 segundos para no saturar la API
                video_file = genai.get_file(video_file.name)
                
            if video_file.state.name == "FAILED":
                raise Exception("El procesamiento del video en los servidores de Google falló.")
                
            print("\n✅ Video procesado. Analizando contenido...")

            respuesta = model.generate_content([video_file, prompt])
            
            genai.delete_file(video_file.name)
            
         
            texto_limpio = respuesta.text.replace('```json', '').replace('```', '').strip()
            return json.loads(texto_limpio)
            
        except Exception as e:
            raise Exception(f"Error en la IA de Video: {str(e)}")
            
        finally:
       
            if temp_video_path and os.path.exists(temp_video_path):
                os.remove(temp_video_path)