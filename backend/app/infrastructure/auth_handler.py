import os
import requests
from jose import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.infrastructure.repositories.usuario_repo import UsuarioRepository # <-- Asegúrate de crear este repo

security = HTTPBearer()

# URL de tu instancia de Clerk (Confirmada)
CLERK_JWKS_URL = "https://cuddly-dory-21.clerk.accounts.dev/.well-known/jwks.json"

# Caché global para las llaves públicas
_jwks_cache = None

def get_jwks():
    """Obtiene las llaves de Clerk con un sistema de caché simple."""
    global _jwks_cache
    if _jwks_cache is None:
        try:
            response = requests.get(CLERK_JWKS_URL)
            response.raise_for_status()
            _jwks_cache = response.json()
        except Exception as e:
            print(f"🚨 Error crítico descargando JWKS: {e}")
            return None
    return _jwks_cache

def get_current_user(res: HTTPAuthorizationCredentials = Depends(security)):
    """Verifica el token de Clerk y retorna el payload del usuario."""

    # Si no hay token (auth desactivada temporalmente), retorna usuario local
    if res is None:
        return {"user_id": "usuario-local"}

    token = res.credentials
    try:
        jwks = requests.get(CLERK_JWKS_URL).json()
        payload = jwt.decode(token, jwks, algorithms=["RS256"], options={"verify_aud": False})
        return payload

    except Exception as e:
        print(f"🚨 Error de Auth Detallado: {str(e)}")
        # Log de seguridad para debuggear en consola
        try:
            headers = jwt.get_unverified_header(token)
            print(f"Token Headers: {headers}")
        except:
            pass
            
        raise HTTPException(
            status_code=401, 
            detail="Tu sesión ha expirado o es inválida. Por favor, inicia sesión de nuevo."
        )