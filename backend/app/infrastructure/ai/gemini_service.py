import google.generativeai as genai
import os
import json
import io
import datetime 
import re
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def analizar_contenido(self, texto: str = None, imagen_bytes: bytes = None):
        fecha_actual = datetime.datetime.now().strftime("%d/%m/%Y")
        prompt = """
Eres un analista experto en verificación de hechos, desinformación y ciberseguridad.
Hoy es FECHA_ACTUAL. Analiza el contenido con rigor profesional y periodístico.

REGLAS CRÍTICAS:
- Si es imagen: extrae TODO el texto visible y analiza también el contexto visual.
- Si es URL: evalúa el enlace como contenido a verificar, identifica dominio, señales de confiabilidad y afirmación central.
- Si es texto: identifica la afirmación principal, hechos verificables, omisiones y lenguaje manipulador.
- score_credibilidad: entero entre 0 y 100. NO uses decimales ni porcentajes.
  * 0–25: Desinformación evidente, fabricación o manipulación grave
  * 26–50: Contenido engañoso, mezcla de hechos y falsedades, contexto distorsionado
  * 51–70: Parcialmente verificable, falta contexto o tiene imprecisiones
  * 71–85: Mayormente verídico, pequeñas imprecisiones o falta de fuentes
  * 86–100: Verificable y confiable con fuentes sólidas
- resultado: "Real" si score > 65, "Fake" si score <= 65
- Sé específico y técnico. Evita respuestas genéricas.
- No agrupes todo en un solo párrafo. Cada campo debe aportar una parte distinta del análisis.
- "detalles" debe tener 2 a 4 párrafos breves separados por saltos de línea, no una lista interminable.
- "indicadores" debe incluir entre 3 y 6 objetos con señales concretas.
- "tecnicas_manipulacion" debe ser una lista de strings; si no aplica, [].

CONSTRUCCIÓN DE FUENTES (obligatorio):
1. Identifica el TEMA PRINCIPAL en máximo 5 palabras.
2. Reemplaza espacios con "+" (ej: "vacuna+covid+efectividad").
3. Construye exactamente estos 3 URLs con ese tema:
   - https://news.google.com/search?q=[TEMA]
   - https://www.google.com/search?q=[TEMA]+fact+check+verdad+falso
   - https://www.google.com/search?q=site:factual.afp.com+OR+site:chequeado.com+OR+site:reuters.com+[TEMA]

Responde ÚNICAMENTE con JSON válido sin markdown ni texto adicional:
{
    "resultado": "Real",
    "score_credibilidad": 78,
    "nivel_credibilidad": "alta",
    "nivel_riesgo": "Bajo",
    "veredicto_corto": "Una sola oración que resume el veredicto final",
    "analisis_contenido": "Descripción objetiva de qué afirma o muestra el contenido analizado",
    "indicadores": [
        {"tipo": "positivo", "descripcion": "Elemento que apoya la veracidad del contenido"},
        {"tipo": "negativo", "descripcion": "Elemento que señala falsedad o manipulación"},
        {"tipo": "neutro", "descripcion": "Dato contextual relevante sin valor de verdad claro"}
    ],
    "contexto_factual": "Contexto histórico, científico o factual necesario para evaluar correctamente el contenido",
    "tecnicas_manipulacion": ["Nombre de técnica detectada si aplica, lista vacía si no hay"],
    "detalles": "Análisis completo y detallado con argumentación técnica sobre cada aspecto del contenido",
    "recomendacion": "Instrucción concreta sobre qué debería hacer el usuario con este contenido",
    "fuentes": [
        {"nombre": "📰 Ver cobertura en Google Noticias", "url": "https://news.google.com/search?q=..."},
        {"nombre": "🔎 Buscar análisis de Fact-Checkers", "url": "https://www.google.com/search?q=..."},
        {"nombre": "🛡️ Verificar en Agencias Oficiales (AFP/Reuters)", "url": "https://www.google.com/search?q=site:factual.afp.com+..."}
    ]
}
""".replace("FECHA_ACTUAL", fecha_actual)
        
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
            respuesta = self.model.generate_content(
                contenido_a_enviar,
                generation_config={
                    "temperature": 0.2,
                    "response_mime_type": "application/json",
                }
            )
            usage = getattr(respuesta, 'usage_metadata', None)
            tokens_used = getattr(usage, 'total_token_count', 0) if usage else 0
            resultado = self._parsear_json_respuesta(respuesta.text)
            resultado['tokens_used'] = tokens_used
            return resultado
        except Exception as e:
            raise Exception(f"Error en la IA: {str(e)}")

    def _parsear_json_respuesta(self, texto_respuesta: str):
        texto_limpio = texto_respuesta.replace('```json', '').replace('```', '').strip()
        try:
            return json.loads(texto_limpio)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", texto_limpio, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise
