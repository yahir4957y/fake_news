# main.py
from fastapi import FastAPI, Depends  # Añade esto aquí
from app.infrastructure.auth_handler import get_current_user

app = FastAPI()  # Tienes que inicializar 'app' antes de usar @app.post

@app.post("/analizar")
async def analizar_contenido(datos: dict, user = Depends(get_current_user)):
    # Si el código llega aquí, es porque el login de Google fue exitoso
    print(f"Usuario verificado: {user['sub']}")
    return {"status": "procesando", "usuario_id": user['sub']}