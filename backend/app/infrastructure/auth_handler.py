import os
import requests
from jose import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.infrastructure.repositories.usuario_repo import UsuarioRepository # <-- Asegúrate de crear este repo

security = HTTPBearer()
user_repo = UsuarioRepository()

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
    token = res.credentials
    jwks = get_jwks()

    if not jwks:
        raise HTTPException(
            status_code=500, 
            detail="Error de configuración en el servidor de autenticación"
        )

    try:
        # 1. Validamos la firma del token
        payload = jwt.decode(
            token, 
            jwks, 
            algorithms=["RS256"], 
            options={
                "verify_aud": False,
                "verify_at_hash": False
            }
        )

        # 2. Extraemos la info del usuario desde el Token
        usuario_id = payload.get("sub") # El ID de Clerk (user_3CEx...)
        
        # Clerk guarda el email y nombre en estos campos del claims
        email = payload.get("email") or payload.get("upn") or "sin_email@app.com"
        nombre = payload.get("name") or "Usuario Nuevo"

        # 3. 🌟 LA SOLUCIÓN PROFESIONAL: Sincronización Just-In-Time
        # Esto evita el error de Foreign Key porque crea al usuario si no existe
        user_repo.asegurar_usuario(
            usuario_id=usuario_id, 
            email=email, 
            nombre=nombre
        )

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