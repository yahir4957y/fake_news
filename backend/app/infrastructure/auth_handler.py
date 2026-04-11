import os
from jose import jwt
import requests
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_JWKS_URL = "https://api.clerk.com/v1/jwks" # Clerk publica sus llaves aquí

def get_current_user(res: HTTPAuthorizationCredentials = Depends(security)):
    token = res.credentials
    try:
        # 1. Obtener las llaves públicas de Clerk para validar el token
        jwks = requests.get(CLERK_JWKS_URL, headers={"Authorization": f"Bearer {CLERK_SECRET_KEY}"}).json()
        
        # 2. Decodificar y validar el token JWT
        # Nota: En producción, deberías cachear el JWKS para no hacer el request cada vez
        payload = jwt.decode(token, jwks, algorithms=["RS256"], options={"verify_aud": False})
        
        return payload  # Aquí vienen los datos del usuario (id, email, etc.)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")