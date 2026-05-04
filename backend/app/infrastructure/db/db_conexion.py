import psycopg2
import os
from dotenv import load_dotenv

# Cargamos las variables de entorno
load_dotenv()

def get_connection():
    # Obtenemos la URL de Supabase desde el .env
    database_url = os.getenv("DATABASE_URL")
    
    try:
        # Nos conectamos usando la URL completa
        conexion = psycopg2.connect(database_url)
        return conexion
    except Exception as e:
        print(f"❌ Error crítico conectando a Supabase: {e}")
        raise e