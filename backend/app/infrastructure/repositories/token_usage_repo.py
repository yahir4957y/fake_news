from app.infrastructure.db.db_conexion import get_connection
from app.domain.schemas import TokenUsageGlobal, TokenUsageUser
from typing import List


class TokenUsageRepository:

    def update_global_usage(self, tokens_used: int):
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                cursor.execute("""
                    UPDATE token_usage_global
                    SET total_tokens_used = total_tokens_used + %s,
                        total_requests    = total_requests + 1,
                        last_updated      = NOW()
                """, (tokens_used,))
                if cursor.rowcount == 0:
                    cursor.execute("""
                        INSERT INTO token_usage_global (total_tokens_used, total_requests, last_updated)
                        VALUES (%s, 1, NOW())
                    """, (tokens_used,))
                conexion.commit()
        except Exception as e:
            print(f"Error actualizando uso global: {e}")
        finally:
            conexion.close()

    def update_user_usage(self, usuario_id: str, email: str, tokens_used: int):
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO token_usage_user (usuario_id, email, tokens_used, requests_count)
                    VALUES (%s, %s, %s, 1)
                    ON CONFLICT (usuario_id) DO UPDATE SET
                        tokens_used    = token_usage_user.tokens_used + %s,
                        requests_count = token_usage_user.requests_count + 1,
                        last_request   = NOW()
                """, (usuario_id, email or "", tokens_used, tokens_used))
                conexion.commit()
        except Exception as e:
            print(f"Error actualizando uso de usuario: {e}")
        finally:
            conexion.close()

    def get_global_usage(self) -> TokenUsageGlobal:
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT id, total_tokens_used, total_requests, last_updated "
                    "FROM token_usage_global LIMIT 1"
                )
                row = cursor.fetchone()
                if row:
                    return TokenUsageGlobal(
                        id=str(row[0]),
                        total_tokens_used=row[1],
                        total_requests=row[2],
                        last_updated=row[3].isoformat() if row[3] else None,
                    )
                return TokenUsageGlobal(total_tokens_used=0, total_requests=0)
        except Exception as e:
            print(f"Error obteniendo uso global: {e}")
            return TokenUsageGlobal(total_tokens_used=0, total_requests=0)
        finally:
            conexion.close()

    def get_user_usage(self, usuario_id: str) -> TokenUsageUser:
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT usuario_id, email, tokens_used, requests_count, last_request "
                    "FROM token_usage_user WHERE usuario_id = %s",
                    (usuario_id,)
                )
                row = cursor.fetchone()
                if row:
                    return TokenUsageUser(
                        usuario_id=row[0],
                        email=row[1] or "",
                        tokens_used=row[2],
                        requests_count=row[3],
                        last_request=row[4].isoformat() if row[4] else None,
                    )
                return TokenUsageUser(usuario_id=usuario_id, email="", tokens_used=0, requests_count=0)
        except Exception as e:
            print(f"Error obteniendo uso de usuario: {e}")
            return TokenUsageUser(usuario_id=usuario_id, email="", tokens_used=0, requests_count=0)
        finally:
            conexion.close()

    def get_all_users_usage(self) -> List[TokenUsageUser]:
        conexion = get_connection()
        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT usuario_id, email, tokens_used, requests_count, last_request "
                    "FROM token_usage_user ORDER BY tokens_used DESC"
                )
                return [
                    TokenUsageUser(
                        usuario_id=row[0],
                        email=row[1] or "",
                        tokens_used=row[2],
                        requests_count=row[3],
                        last_request=row[4].isoformat() if row[4] else None,
                    )
                    for row in cursor.fetchall()
                ]
        except Exception as e:
            print(f"Error obteniendo todos los usuarios: {e}")
            return []
        finally:
            conexion.close()
