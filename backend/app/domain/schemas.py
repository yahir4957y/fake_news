from pydantic import BaseModel
from typing import Optional

class AnalisisRequest(BaseModel):
    tipo: str  # Puede ser: 'texto', 'imagen', 'video', 'url'
    texto: Optional[str] = None
    url: Optional[str] = None
    # Nota: Por ahora ignoramos usuario_id hasta que sincronicemos los usuarios de Clerk con tu BD.