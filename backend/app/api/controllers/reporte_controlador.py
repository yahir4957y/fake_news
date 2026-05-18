from fastapi import HTTPException
from fastapi.responses import FileResponse
from app.application.use_cases.reporte_servicio import ReporteService
from app.infrastructure.repositories.reporte_repositorio import ReportesRepositorio as ReportesRepository
from app.domain.reporte_esquemas import ListaAnalisisResponse, AnalisisParaExportar
from datetime import datetime

class ReportesControlador:
    """Controlador para gestionar reportes y exportaciones de análisis"""
    
    def __init__(self):
        # NUEVO: Inicializa el servicio de reportes y repositorio
        self.servicio = ReporteService()
        self.repo = ReportesRepository()
    
    def obtener_analisis_usuario(self, usuario_id: str):
        """NUEVO: Obtiene lista de análisis disponibles para exportar del usuario autenticado"""
        try:
            # NUEVO: Consulta BD para obtener análisis
            analisis_list = self.repo.obtener_analisis_usuario(usuario_id)
            
            # NUEVO: Transforma datos a modelo Pydantic
            analisis_formateado = [
                AnalisisParaExportar(
                    verificacion_id=a['verificacion_id'],
                    contenido_tipo=a['contenido_tipo'],
                    contenido_preview=a['contenido_preview'],
                    resultado=a['resultado'],
                    score_credibilidad=a['score_credibilidad'],
                    fecha=a['fecha']
                )
                for a in analisis_list
            ]
            
            # NUEVO: Retorna respuesta con total y lista
            return ListaAnalisisResponse(
                total=len(analisis_formateado),
                analisis=analisis_formateado
            )
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error obteniendo análisis: {str(e)}")
    
    def generar_y_descargar_reporte(self, usuario_id: str, verificacion_id: str, formato: str):
        """NUEVO: Genera reporte en formato especificado y retorna archivo para descargar"""
        # NUEVO: Valida formato permitido
        if formato not in ['pdf', 'csv']:
            raise HTTPException(status_code=400, detail="Formato debe ser 'pdf' o 'csv'")
        
        try:
            # NUEVO: Genera reporte usando servicio
            resultado = self.servicio.generar_reporte(usuario_id, verificacion_id, formato)
            
            archivo_path = resultado['archivo_path']
            archivo_nombre = resultado['archivo_nombre']
            
            # Registra exportación en BD para auditoría (no es crítico)
            try:
                self.repo.guardar_reporte_exportado(
                    usuario_id,
                    verificacion_id,
                    formato,
                    archivo_path,
                    archivo_nombre
                )
            except Exception as audit_err:
                print(f"⚠️ No se pudo registrar en reports_export: {audit_err}")
            
            # NUEVO: Determina tipo MIME según formato
            media_type = "application/pdf" if formato == "pdf" else "text/csv"
            
            # NUEVO: Retorna archivo para descargar
            return FileResponse(
                path=archivo_path,
                media_type=media_type,
                filename=archivo_nombre,
                headers={"Content-Disposition": f"attachment; filename={archivo_nombre}"}
            )
        
        except ValueError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generando reporte: {str(e)}")
