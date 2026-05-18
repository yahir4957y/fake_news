from fastapi import APIRouter, Depends, HTTPException
from app.infrastructure.auth_handler import get_current_user
from app.application.use_cases.manage_token_usage import ManageTokenUsage
from app.infrastructure.repositories.token_usage_repo import TokenUsageRepository

router = APIRouter(prefix="/api/tokens", tags=["tokens"])
token_repo = TokenUsageRepository()
token_manager = ManageTokenUsage(token_repo)

@router.get("/my-stats")
def get_my_stats(user=Depends(get_current_user)):
    """Obtener estadísticas de tokens del usuario actual"""
    try:
        usuario_id = user.get("sub")  # ID de Clerk
        email = user.get("email")
        stats = token_manager.get_user_stats(usuario_id)
        return {
            "success": True,
            "data": {
                "usuario_id": usuario_id,
                "email": email,
                "tokens_used": stats.tokens_used,
                "requests_count": stats.requests_count,
                "last_request": stats.last_request
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/global-stats")
def get_global_stats(user=Depends(get_current_user)):
    """Obtener estadísticas globales (solo verificar autenticación)"""
    try:
        stats = token_manager.get_global_stats()
        return {
            "success": True,
            "data": {
                "total_tokens_used": stats.total_tokens_used,
                "total_requests": stats.total_requests
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all-users-stats")
def get_all_users_stats(user=Depends(get_current_user)):
    """Obtener estadísticas de todos los usuarios (mostrar en tabla)"""
    try:
        stats = token_manager.get_all_users_stats()
        return {
            "success": True,
            "data": [
                {
                    "email": s.email,
                    "tokens_used": s.tokens_used,
                    "requests_count": s.requests_count,
                    "last_request": s.last_request
                }
                for s in stats
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))