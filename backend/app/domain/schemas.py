from pydantic import BaseModel
from typing import Optional

class AnalisisRequest(BaseModel):
    tipo: str  # Puede ser: 'texto', 'imagen', 'video', 'url'
    texto: Optional[str] = None
    url: Optional[str] = None

class TokenUsageGlobal(BaseModel):
    id: Optional[str] = None
    total_tokens_used: int = 0
    total_requests: int = 0
    last_updated: Optional[str] = None

class TokenUsageUser(BaseModel):
    usuario_id: str
    email: str = ""
    tokens_used: int = 0
    requests_count: int = 0
    last_request: Optional[str] = None
  
