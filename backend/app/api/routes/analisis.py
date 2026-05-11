# backend/app/api/routes/analisis.py
# Capa de API — Rutas de análisis de contenido

from fastapi import APIRouter, HTTPException, Depends
from app.infrastructure.auth_handler import get_current_user

router = APIRouter(prefix="/api/analisis", tags=["Analisis"])

# TODO: agregar endpoints de análisis (texto, URL, imagen)