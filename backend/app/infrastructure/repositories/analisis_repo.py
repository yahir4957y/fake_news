# backend/app/infrastructure/repositories/analisis_repo.py
from app.infrastructure.db.db_conexion import get_supabase
from datetime import datetime, timedelta

class AnalisisRepository:
    def __init__(self):
        self.supabase = get_supabase()

    def obtener_todos(self) -> list:
        try:
            response = self.supabase.table("analisis").select("*").execute()
            return response.data or []
        except Exception as e:
            raise Exception(f"Error en AnalisisRepository.obtener_todos: {str(e)}")

    def _parse_fecha(self, fecha_str: str) -> datetime | None:
        """Parsea fechas de Supabase tolerando microsegundos variables."""
        if not fecha_str:
            return None
        try:
            # Normaliza microsegundos a 6 dígitos
            fecha_str = fecha_str.replace("Z", "")
            if "." in fecha_str:
                base, micro = fecha_str.split(".")
                micro = micro.ljust(6, "0")[:6]
                fecha_str = f"{base}.{micro}"
            return datetime.fromisoformat(fecha_str)
        except Exception:
            return None

    def obtener_metricas(self) -> dict:
        try:
            # Total de usuarios
            try:
                usuarios_resp = self.supabase.table("usuarios").select("id").execute()
                total_usuarios = len(usuarios_resp.data or [])
            except Exception:
                total_usuarios = 0

            # Contenidos
            try:
                contenidos_resp = self.supabase.table("contenidos").select("id, creado_en, tipo").execute()
                contenidos = contenidos_resp.data or []
                total_contenidos = len(contenidos)
            except Exception:
                contenidos = []
                total_contenidos = 0

            # Contenidos por tipo
            tipo_map = {}
            for c in contenidos:
                t = c.get("tipo") or "otro"
                tipo_map[t] = tipo_map.get(t, 0) + 1

            contenidos_por_tipo = [
                {"tipo": t, "cantidad": n}
                for t, n in sorted(tipo_map.items(), key=lambda x: x[1], reverse=True)
            ]

            # Solicitudes por hora (últimas 12h)
            ahora = datetime.utcnow()
            horas = []
            for i in range(11, -1, -1):
                hora_inicio = ahora - timedelta(hours=i+1)
                hora_fin    = ahora - timedelta(hours=i)
                count = 0
                for c in contenidos:
                    fecha = self._parse_fecha(c.get("creado_en"))
                    if fecha and hora_inicio <= fecha < hora_fin:
                        count += 1
                horas.append({
                    "hora": f"{hora_fin.hour}h",
                    "solicitudes": count
                })

            return {
                "total_usuarios": total_usuarios,
                "total_contenidos": total_contenidos,
                "contenidos_por_tipo": contenidos_por_tipo,
                "solicitudes_por_hora": horas,
            }

        except Exception as e:
            raise Exception(f"Error en AnalisisRepository.obtener_metricas: {str(e)}")