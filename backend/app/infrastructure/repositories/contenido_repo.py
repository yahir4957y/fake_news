from app.infrastructure.db.db_conexion import get_connection

class ContenidoRepository:
    def guardar_contenido(self, tipo: str, texto: str = None, url: str = None, usuario_id: str = None):
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                # Insertamos con el usuario_id y estado inicial "pendiente"
                query = """
                    INSERT INTO contenidos (tipo, texto, url, usuario_id, estado)
                    VALUES (%s, %s, %s, %s, 'pendiente')
                    RETURNING id;
                """
                cursor.execute(query, (tipo, texto, url, usuario_id))
                contenido_id = cursor.fetchone()[0]
                conexion.commit()
                return contenido_id
        except Exception as e:
            print(f"Error al guardar en BD: {e}")
            raise e
        finally:
            conexion.close()

    # 🌟 NUEVA FUNCIÓN para cambiar el estado de 'pendiente' a 'completado' o 'error'
    def actualizar_estado(self, contenido_id: str, nuevo_estado: str):
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                query = "UPDATE contenidos SET estado = %s WHERE id = %s;"
                cursor.execute(query, (nuevo_estado, contenido_id))
                conexion.commit()
        finally:
            conexion.close()