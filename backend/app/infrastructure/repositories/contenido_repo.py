from app.infrastructure.db.db_conexion import get_supabase

class ContenidoRepository:
    def __init__(self):
        self.supabase = get_supabase()

    def guardar_contenido(self, tipo: str, texto: str = None, url: str = None) -> str:
        """Guarda un contenido en Supabase y retorna su ID."""
        try:    
            response = self.supabase.table("contenidos").insert({
                "tipo": tipo,
                "texto": texto,
                "url": url,
                "estado": "pendiente"
            }).execute()

            if response.data:
                return response.data[0]["id"]
            raise Exception("No se pudo guardar el contenido en Supabase")

        except Exception as e:
            raise Exception(f"Error en ContenidoRepository.guardar_contenido: {str(e)}")