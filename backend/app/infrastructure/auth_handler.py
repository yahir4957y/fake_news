import os
from jose import jwt
import requests
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

CLERK_JWKS_URL = "https://cuddly-dory-21.clerk.accounts.dev/.well-known/jwks.json"

def get_current_user(res: HTTPAuthorizationCredentials = Depends(security)):
    token = res.credentials
    try:
        jwks = requests.get(CLERK_JWKS_URL).json()
        payload = jwt.decode(token, jwks, algorithms=["RS256"], options={"verify_aud": False})
        return payload
    except Exception as e:
        print(f"Error de Auth: {str(e)}")
        raise HTTPException(status_code=401, detail="Token inválido o expirado")