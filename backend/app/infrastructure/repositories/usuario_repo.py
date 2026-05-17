from app.infrastructure.db.db_conexion import get_connection

class UsuarioRepository:
    def asegurar_usuario(self, usuario_id: str, email: str, nombre: str):
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                query = """
                    INSERT INTO usuarios (id, email, nombre)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (id) DO UPDATE 
                    SET email = EXCLUDED.email, 
                        nombre = EXCLUDED.nombre;
                """
                cursor.execute(query, (usuario_id, email, nombre))
                conexion.commit()
        except Exception as e:
            print(f"🚨 Error al sincronizar usuario: {e}")
            conexion.rollback()
        finally:
            conexion.close()