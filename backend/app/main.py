from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import analisis

app = FastAPI(title="FakeNewsAI Backend")

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "API online y conectada a la matrix"}

# Conectar el router (la ruta será http://localhost:8000/api/analisis/)
app.include_router(analisis.router)