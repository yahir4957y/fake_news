from app.infrastructure.repositories.token_usage_repo import TokenUsageRepository
from app.domain.schemas import TokenUsageGlobal, TokenUsageUser
from typing import List

class ManageTokenUsage:
    def __init__(self, repo: TokenUsageRepository):
        self.repo = repo

    def record_usage(self, usuario_id: str, email: str, tokens_used: int):
        """Registrar uso de tokens cuando se hace un análisis"""
        self.repo.update_global_usage(tokens_used)
        self.repo.update_user_usage(usuario_id, email, tokens_used)

    def get_global_stats(self) -> TokenUsageGlobal:
        """Obtener estadísticas globales del sistema"""
        return self.repo.get_global_usage()

    def get_user_stats(self, usuario_id: str) -> TokenUsageUser:
        """Obtener estadísticas del usuario actual"""
        return self.repo.get_user_usage(usuario_id)

    def get_all_users_stats(self) -> List[TokenUsageUser]:
        """Obtener estadísticas de todos los usuarios"""
        return self.repo.get_all_users_usage()