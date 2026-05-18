from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AnalisisParaExportar(BaseModel):
    verificacion_id: str
    contenido_tipo: str
    contenido_preview: str
    resultado: str
    score_credibilidad: float
    fecha: datetime

class ReporteExportarRequest(BaseModel):
    verificacion_id: str
    formato: str  # 'pdf' o 'csv'

class ReporteExportarResponse(BaseModel):
    id: str
    estado: str
    archivo_url: str
    archivo_nombre: str
    creado_en: datetime
    formato: str

class ListaAnalisisResponse(BaseModel):
    total: int
    analisis: List[AnalisisParaExportar]
