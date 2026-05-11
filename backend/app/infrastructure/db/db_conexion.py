import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

def get_supabase() -> Client:
    """Retorna el cliente de Supabase listo para usar."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise Exception(
            "Faltan variables SUPABASE_URL o SUPABASE_SERVICE_KEY en el .env"
        )
    return create_client(SUPABASE_URL, SUPABASE_KEY)
