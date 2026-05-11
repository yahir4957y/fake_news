import uuid
from app.infrastructure.db.db_conexion import get_supabase

class UsuariosRepository:
    def __init__(self):
        self.supabase = get_supabase()

    def obtener_todos(self) -> list:
        """Retorna todos los usuarios."""
        try:
            response = self.supabase.table("usuarios").select("*").execute()
            return response.data or []
        except Exception as e:
            raise Exception(f"Error en UsuariosRepository.obtener_todos: {str(e)}")

    def obtener_por_id(self, usuario_id: str) -> dict:
        """Retorna un usuario por su ID."""
        try:
            response = self.supabase.table("usuarios").select("*").eq("id", usuario_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Error en UsuariosRepository.obtener_por_id: {str(e)}")

    def crear(self, nombre: str, email: str, foto_url: str = None, proveedor_auth: str = "clerk") -> dict:
        """Crea un nuevo usuario y retorna el registro creado."""
        try:
            response = self.supabase.table("usuarios").insert({
                "id": str(uuid.uuid4()),
                "nombre": nombre,
                "email": email,
                "foto_url": foto_url,
                "proveedor_auth": proveedor_auth
            }).execute()

            if response.data:
                return response.data[0]
            raise Exception("No se pudo crear el usuario")
        except Exception as e:
            raise Exception(f"Error en UsuariosRepository.crear: {str(e)}")

    def actualizar(self, usuario_id: str, nombre: str, email: str, foto_url: str = None, proveedor_auth: str = "clerk") -> dict:
        """Actualiza un usuario existente."""
        try:
            response = self.supabase.table("usuarios").update({
                "nombre": nombre,
                "email": email,
                "foto_url": foto_url,
                "proveedor_auth": proveedor_auth
            }).eq("id", usuario_id).execute()

            if response.data:
                return response.data[0]
            raise Exception("Usuario no encontrado")
        except Exception as e:
            raise Exception(f"Error en UsuariosRepository.actualizar: {str(e)}")

    def eliminar(self, usuario_id: str) -> bool:
        """Elimina un usuario por su ID."""
        try:
            self.supabase.table("usuarios").delete().eq("id", usuario_id).execute()
            return True
        except Exception as e:
            raise Exception(f"Error en UsuariosRepository.eliminar: {str(e)}")