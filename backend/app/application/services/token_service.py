from app.infrastructure.repositories.token_usage_repo import TokenUsageRepository
from app.application.use_cases.manage_token_usage import ManageTokenUsage


class TokenService:

    def __init__(self):
        self.token_manager = ManageTokenUsage(TokenUsageRepository())

    def registrar_consumo(self, analisis_ia, usuario_uuid, user):

        tokens_used = analisis_ia.pop("tokens_used", 0)

        try:
            self.token_manager.record_usage(
                usuario_id=usuario_uuid,
                email=user.get("email") or "",
                tokens_used=tokens_used
            )

        except Exception as token_err:
            print(f"⚠️ No se pudo registrar uso de tokens: {token_err}")