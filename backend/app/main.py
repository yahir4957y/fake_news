from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import analisis, reporte_rutas, tokens

app = FastAPI(title="FakeNewsAI Backend")

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "API online y conectada a la matrix"}

app.include_router(analisis.router)
app.include_router(reporte_rutas.router)
app.include_router(tokens.router)
