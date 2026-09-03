import requests
import os
import logging
from app.interfaces.channel_sender_interface import IChannelSender

logger = logging.getLogger(__name__)


class WhatsAppSender(IChannelSender):
    def __init__(self):
        self.token = os.environ["WHATSAPP_ACCESS_TOKEN"]
        self.phone_number_id = os.environ["WHATSAPP_PHONE_NUMBER_ID"]
        self.base_url = f"https://graph.facebook.com/v19.0/{self.phone_number_id}/messages"

    def send(self, destinataire: str, message: str) -> dict:
        if not destinataire:
            return {"statut": "echec", "raison": "Aucun numéro WhatsApp fourni pour ce prospect"}

        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        payload = {
            "messaging_product": "whatsapp",
            "to": destinataire,
            "type": "text",
            "text": {"body": message}
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=10)

            if response.status_code == 200:
                logger.info(f"Message WhatsApp envoyé à {destinataire}")
                return {"statut": "envoye"}

            logger.warning(f"Échec envoi WhatsApp à {destinataire} : {response.status_code} - {response.text}")
            return {"statut": "echec", "raison": self._traduire_erreur(response)}

        except requests.exceptions.Timeout:
            return {"statut": "echec", "raison": "Timeout lors de l'envoi WhatsApp"}
        except Exception as e:
            logger.error(f"Erreur inattendue envoi WhatsApp à {destinataire} : {e}", exc_info=True)
            return {"statut": "echec", "raison": f"Erreur technique : {e}"}

    def _traduire_erreur(self, response):
        """Rend l'erreur Meta lisible plutôt que de renvoyer le JSON brut."""
        try:
            detail = response.json().get("error", {})
            code = detail.get("code")
            message = detail.get("message", "Erreur inconnue")

            if code == 131030:
                return "Ce numéro n'est pas autorisé en mode test (ajoutez-le dans les destinataires de test Meta)."
            if code == 131047:
                return "Fenêtre de conversation de 24h expirée : un template pré-approuvé est nécessaire."
            if code == 190:
                return "Token d'accès invalide ou expiré."
            return message
        except Exception:
            return response.text[:200]