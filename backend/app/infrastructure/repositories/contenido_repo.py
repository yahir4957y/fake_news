import json
from app.infrastructure.db.db_conexion import get_connection

class ContenidoRepository:
    
    def guardar_contenido(self, tipo: str, texto: str = None, url: str = None, usuario_id: str = None, ip_usuario: str = None, dispositivo: str = None, hash_archivo: str = None):
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                query_contenido = """
                    INSERT INTO contenidos (tipo, texto, url, usuario_id, estado, hash_archivo)
                    VALUES (%s, %s, %s, %s, 'pendiente', %s)
                    RETURNING id;
                """
                cursor.execute(query_contenido, (tipo, texto, url, usuario_id, hash_archivo))
                contenido_id = cursor.fetchone()[0]

                query_verificacion = """
                    INSERT INTO verificaciones 
                    (usuario_id, contenido_id, tipo_verificacion, estado, ip_usuario, dispositivo)
                    VALUES (%s, %s, %s, 'en_proceso', %s, %s);
                """
                cursor.execute(query_verificacion, (usuario_id, contenido_id, tipo, ip_usuario, dispositivo))

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
                query_cont = "UPDATE contenidos SET estado = %s WHERE id = %s;"
                cursor.execute(query_cont, (nuevo_estado, contenido_id))
                
                query_verif = "UPDATE verificaciones SET estado = %s WHERE contenido_id = %s;"
                cursor.execute(query_verif, (nuevo_estado, contenido_id))
                
                conexion.commit()
        except Exception as e:
            print(f"Error al actualizar estado: {e}")
            conexion.rollback()
            raise e
        finally:
            conexion.close()

    def finalizar_verificacion(self, contenido_id: str, score: float, nivel: str, estado_final: str):
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "UPDATE contenidos SET estado = %s WHERE id = %s;",
                    (estado_final, contenido_id)
                )
                
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
            

    def guardar_retroalimentacion(self, contenido_id: str, detalles: str, recomendacion: str, fuentes: list, modelo_ia: str = "gemini-2.5-flash"):
        """
        Guarda la justificación textual y las fuentes de la IA en la tabla retroalimentacion_ia.
        """
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
          
                cursor.execute("SELECT id FROM verificaciones WHERE contenido_id = %s", (contenido_id,))
                verificacion = cursor.fetchone()

                if verificacion:
                    verificacion_id = verificacion[0]
                    
                   
                    query = """
                        INSERT INTO retroalimentacion_ia 
                        (verificacion_id, resumen, recomendacion, fuentes_sugeridas, modelo_ia)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                   
                    fuentes_json = json.dumps(fuentes) if fuentes else '[]'
                    
                    cursor.execute(query, (verificacion_id, detalles, recomendacion, fuentes_json, modelo_ia))
                    conexion.commit()
                    print("✅ Retroalimentación guardada en BD exitosamente.")
        except Exception as e:
            print(f"🚨 Error al guardar retroalimentación en BD: {e}")
            conexion.rollback()
        finally:
            conexion.close()

    def obtener_historial_por_usuario(self, usuario_id: str):
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                query = """
                    SELECT 
                        c.tipo,
                        c.creado_en as fecha,
                        c.estado,
                        v.score_credibilidad as confidence,
                        r.resumen as details,
                        r.recomendacion,
                        r.fuentes_sugeridas as fuentes
                    FROM contenidos c
                    LEFT JOIN verificaciones v ON v.contenido_id = c.id
                    LEFT JOIN retroalimentacion_ia r ON r.verificacion_id = v.id
                    WHERE c.usuario_id = %s
                    ORDER BY c.creado_en DESC;
                """
                cursor.execute(query, (usuario_id,))
                columnas = [desc[0] for desc in cursor.description]
                return [dict(zip(columnas, row)) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error al obtener el historial: {e}")
            return []
        finally:
            conexion.close()