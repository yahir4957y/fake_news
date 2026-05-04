from app.infrastructure.db.db_conexion import get_connection

class ContenidoRepository:
    # 🔥 1. ACTUALIZADO: Agregamos hash_archivo al final
    def guardar_contenido(self, tipo: str, texto: str = None, url: str = None, usuario_id: str = None, ip_usuario: str = None, dispositivo: str = None, hash_archivo: str = None):
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                # Insertamos en 'contenidos' incluyendo el hash
                query_contenido = """
                    INSERT INTO contenidos (tipo, texto, url, usuario_id, estado, hash_archivo)
                    VALUES (%s, %s, %s, %s, 'pendiente', %s)
                    RETURNING id;
                """
                cursor.execute(query_contenido, (tipo, texto, url, usuario_id, hash_archivo))
                contenido_id = cursor.fetchone()[0]

                # Insertamos la verificación inicial con la IP y el Dispositivo
                query_verificacion = """
                    INSERT INTO verificaciones 
                    (usuario_id, contenido_id, tipo_verificacion, estado, ip_usuario, dispositivo)
                    VALUES (%s, %s, %s, 'en_proceso', %s, %s);
                """
                cursor.execute(query_verificacion, (usuario_id, contenido_id, tipo, ip_usuario, dispositivo))

                # Guardamos los cambios
                conexion.commit()
                return contenido_id
        except Exception as e:
            print(f"Error al guardar en BD: {e}")
            conexion.rollback()
            raise e
        finally:
            conexion.close()

    def actualizar_estado(self, contenido_id: str, nuevo_estado: str):
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                # Actualizamos el estado en contenidos
                query_cont = "UPDATE contenidos SET estado = %s WHERE id = %s;"
                cursor.execute(query_cont, (nuevo_estado, contenido_id))
                
                # Sincronizamos el estado en verificaciones
                query_verif = "UPDATE verificaciones SET estado = %s WHERE contenido_id = %s;"
                cursor.execute(query_verif, (nuevo_estado, contenido_id))
                
                conexion.commit()
        finally:
            conexion.close()

    def finalizar_verificacion(self, contenido_id: str, score: float, nivel: str, estado_final: str):
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                # 1. Actualizamos el estado en la tabla contenidos
                cursor.execute(
                    "UPDATE contenidos SET estado = %s WHERE id = %s;",
                    (estado_final, contenido_id)
                )
                
                # 2. Llenamos TODOS los datos en verificaciones y cerramos la fecha
                query_verif = """
                    UPDATE verificaciones 
                    SET 
                        estado = %s,
                        score_credibilidad = %s,
                        nivel_credibilidad = %s,
                        fecha_fin = NOW()
                    WHERE contenido_id = %s;
                """
                cursor.execute(query_verif, (estado_final, score, nivel, contenido_id))
                
                conexion.commit()
        except Exception as e:
            print(f"Error al finalizar verificación: {e}")
            conexion.rollback()
            raise e
        finally:
            conexion.close()

    # 🔥 2. NUEVA FUNCIÓN: Busca en la base de datos si la imagen ya fue analizada
    def buscar_por_hash(self, hash_archivo: str):
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                query = """
                    SELECT v.score_credibilidad, v.nivel_credibilidad, c.estado 
                    FROM contenidos c
                    JOIN verificaciones v ON c.id = v.contenido_id
                    WHERE c.hash_archivo = %s AND c.estado IN ('verificado', 'desmentido')
                    LIMIT 1;
                """
                cursor.execute(query, (hash_archivo,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error al buscar por hash: {e}")
            return None
        finally:
            conexion.close()