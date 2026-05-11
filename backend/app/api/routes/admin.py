from fastapi import APIRouter, HTTPException, Depends
from app.infrastructure.repositories.analisis_repo import AnalisisRepository
from app.infrastructure.auth_handler import get_current_user

router = APIRouter(prefix="/api/admin", tags=["Admin"])

analisis_repo = AnalisisRepository()

@router.get("/metricas")
def obtener_metricas(user=Depends(get_current_user)):
    """Retorna métricas generales del dashboard de administrador."""
    try:
        return analisis_repo.obtener_metricas()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))