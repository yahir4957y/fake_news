from app.infrastructure.db.db_conexion import get_supabase

class ContenidoRepository:
    def guardar_contenido(self, tipo: str, texto: str = None, url: str = None):
        conexion = get_connection()
        cursor = conexion.cursor()
        
        try:

            query = """
                INSERT INTO contenidos (tipo, texto, url, estado)
                VALUES (%s, %s, %s, 'pendiente')
                RETURNING id;
            """
            cursor.execute(query, (tipo, texto, url))
            nuevo_id = cursor.fetchone()[0] # Obtenemos el UUID generado
            
            conexion.commit()
            return nuevo_id
            
        except Exception as e:
            conexion.rollback()
            raise Exception(f"Error al guardar en BD: {str(e)}")
            
        finally:
            cursor.close()
            conexion.close()