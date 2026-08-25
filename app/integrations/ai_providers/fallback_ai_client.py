from app.interfaces.ai_provider_interface import IAIMessageGenerator
from app.integrations.ai_providers.dto import GeneratedMessage

class FallbackAIClient(IAIMessageGenerator):
    """Essaie plusieurs providers dans l'ordre, en cas d'échec ou de quota dépassé"""
    def __init__(self, providers: list):
        self.providers = providers

    def generate(self, system_prompt, user_prompt, channel) -> GeneratedMessage:
        derniere_erreur = None
        for provider in self.providers:
            try:
                return provider.generate(system_prompt, user_prompt, channel)
            except Exception as e:
                derniere_erreur = e
                continue
        raise Exception(f"Tous les providers IA ont échoué. Dernière erreur : {derniere_erreur}")