import os
from jose import jwt
import requests
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)

CLERK_JWKS_URL = "https://cuddly-dory-21.clerk.accounts.dev/.well-known/jwks.json"

def get_current_user(res: HTTPAuthorizationCredentials = Depends(security)):
    """Verifica el token de Clerk y retorna el payload del usuario."""

    # Si no hay token (auth desactivada temporalmente), retorna usuario local
    if res is None:
        return {"user_id": "usuario-local"}

    token = res.credentials
    try:
        jwks = requests.get(CLERK_JWKS_URL).json()
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            options={"verify_aud": False}
        )
        return payload
    except Exception as e:
        print(f"Error de Auth: {str(e)}")
        raise HTTPException(status_code=401, detail="Token inválido o expirado")