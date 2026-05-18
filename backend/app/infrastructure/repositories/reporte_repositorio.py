import json
from app.infrastructure.db.db_conexion import get_connection
from datetime import datetime

class ReportesRepositorio:
    """Repositorio para consultas de reportes y exportaciones"""

    def obtener_analisis_usuario(self, usuario_id: str):
        """NUEVO: Recupera los análisis del usuario para mostrar en la tabla de reportes"""
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                query = """
                    SELECT 
                        v.id as verificacion_id,
                        c.tipo as contenido_tipo,
                        COALESCE(c.texto, c.url, 'Multimedia') as contenido_preview,
                        CASE 
                            WHEN v.estado = 'verificado' THEN 'Real'
                            WHEN v.estado = 'desmentido' THEN 'Fake'
                            ELSE v.estado
                        END as resultado,
                        v.score_credibilidad,
                        COALESCE(v.fecha_fin, v.fecha_inicio, c.creado_en) as fecha,
                        r.resumen,
                        r.recomendacion,
                        r.fuentes_sugeridas
                    FROM verificaciones v
                    JOIN contenidos c ON v.contenido_id = c.id
                    LEFT JOIN retroalimentacion_ia r ON v.id = r.verificacion_id
                    WHERE v.usuario_id = %s
                    ORDER BY COALESCE(v.fecha_fin, v.fecha_inicio, c.creado_en) DESC
                    LIMIT 1000
                """
                cursor.execute(query, (usuario_id,))
                resultados = cursor.fetchall()
                
                return [
                    {
                        'verificacion_id': str(r[0]),
                        'contenido_tipo': r[1],
                        'contenido_preview': str(r[2])[:100] if r[2] else 'N/A',
                        'resultado': r[3],
                        'score_credibilidad': float(r[4]) if r[4] else 0,
                        'fecha': r[5],
                        'resumen': r[6],
                        'recomendacion': r[7],
                        'fuentes_sugeridas': r[8] if r[8] else []
                    }
                    for r in resultados
                ]
        finally:
            conexion.close()

    def obtener_detalle_analisis(self, verificacion_id: str, usuario_id: str):
        """NUEVO: Recupera datos completos de un análisis para generar reporte"""
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                query = """
                    SELECT 
                        v.id,
                        v.usuario_id,
                        v.contenido_id,
                        v.estado,
                        v.score_credibilidad,
                        v.nivel_credibilidad,
                        v.fecha_inicio,
                        v.fecha_fin,
                        c.tipo as contenido_tipo,
                        c.texto,
                        c.url,
                        r.resumen,
                        r.recomendacion,
                        r.fuentes_sugeridas,
                        r.modelo_ia,
                        u.email,
                        u.nombre
                    FROM verificaciones v
                    JOIN contenidos c ON v.contenido_id = c.id
                    LEFT JOIN retroalimentacion_ia r ON v.id = r.verificacion_id
                    JOIN usuarios u ON v.usuario_id = u.id
                    WHERE v.id = %s AND v.usuario_id = %s
                """
                cursor.execute(query, (verificacion_id, usuario_id))
                resultado = cursor.fetchone()
                
                if not resultado:
                    return None
                
                return {
                    'verificacion_id': str(resultado[0]),
                    'usuario_id': str(resultado[1]),
                    'contenido_id': str(resultado[2]),
                    'estado': resultado[3],
                    'score_credibilidad': float(resultado[4]) if resultado[4] else 0,
                    'nivel_credibilidad': resultado[5],
                    'fecha_inicio': resultado[6],
                    'fecha_fin': resultado[7],
                    'contenido_tipo': resultado[8],
                    'contenido_texto': resultado[9],
                    'contenido_url': resultado[10],
                    'resumen': resultado[11],
                    'recomendacion': resultado[12],
                    'fuentes_sugeridas': resultado[13] if resultado[13] else [],
                    'modelo_ia': resultado[14],
                    'email_usuario': resultado[15],
                    'nombre_usuario': resultado[16]
                }
        finally:
            conexion.close()

    def guardar_reporte_exportado(self, usuario_id: str, verificacion_id: str, formato: str, archivo_url: str, archivo_nombre: str) -> str:
        """NUEVO: Guarda registro de exportación para auditoría y seguimiento"""
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                query = """
                    INSERT INTO reports_export 
                        (usuario_id, verificacion_id, formato, archivo_url, archivo_nombre, estado)
                    VALUES (%s, %s, %s, %s, %s, 'generado')
                    RETURNING id
                """
                cursor.execute(query, (usuario_id, verificacion_id, formato, archivo_url, archivo_nombre))
                reporte_id = cursor.fetchone()[0]
                conexion.commit()
                return str(reporte_id)
        except Exception as e:
            print(f"Error al guardar reporte: {e}")
            raise
        finally:
            conexion.close()

    def marcar_descargado(self, reporte_id: str):
        """NUEVO: Marca la exportación como descargada"""
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                query = """
                    UPDATE reports_export 
                    SET estado = 'descargado', descargado_en = NOW()
                    WHERE id = %s
                """
                cursor.execute(query, (reporte_id,))
                conexion.commit()
        finally:
            conexion.close()
