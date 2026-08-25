from abc import ABC, abstractmethod

class IChannelSender(ABC):
    @abstractmethod
    def send(self, destinataire: str, message: str) -> dict:
        """Retourne {"statut": "envoye"|"echec", "raison": str (optionnel)}"""
        ...