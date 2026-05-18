from fastapi import APIRouter, Depends, HTTPException, Query
from app.infrastructure.auth_handler import get_current_user
from app.api.controllers.reporte_controlador import ReportesControlador

# NUEVO: Router para endpoints de reportes
router = APIRouter(prefix="/api/reportes", tags=["Reportes"])

# NUEVO: Instancia del controlador
controlador = ReportesControlador()


@router.get("/")
async def obtener_analisis_para_exportar(user=Depends(get_current_user)):
    """
    NUEVO: Obtiene lista de análisis del usuario disponibles para exportar en PDF/CSV
    
    Parámetros:
    - user: Usuario autenticado vía Clerk (automático)
    
    Retorna: {total: int, analisis: List[AnalisisParaExportar]}
    """
    usuario_id = user.get("sub")
    
    # NUEVO: Llama controlador para obtener análisis
    return controlador.obtener_analisis_usuario(usuario_id)


@router.get("/descargar/{verificacion_id}")
async def descargar_reporte(
    verificacion_id: str,
    formato: str = Query(..., pattern="^(pdf|csv)$"),
    user=Depends(get_current_user)
):
    """
    NUEVO: Genera y descarga reporte en formato especificado (PDF o CSV)
    
    Parámetros:
    - verificacion_id: ID del análisis a exportar
    - formato: 'pdf' o 'csv' (query param)
    - user: Usuario autenticado vía Clerk (automático)
    
    Retorna: Archivo descargable (PDF o CSV)
    """
    usuario_id = user.get("sub")
    
    # NUEVO: Llama controlador para generar y descargar reporte
    return controlador.generar_y_descargar_reporte(usuario_id, verificacion_id, formato)
