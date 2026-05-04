import google.generativeai as genai
import os
from dotenv import load_dotenv

# Cargar tu llave
load_dotenv()
genai.configure(api_key=os.getenv("AIzaSyBTQAMP7fxTXYzrXex2QlCiV57jtFNmpXY"))

print("Buscando modelos disponibles para tu API Key...\n")

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Modelo compatible: {m.name}")
except Exception as e:
    print(f"Error al conectar: {e}")