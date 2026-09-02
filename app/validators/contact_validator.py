import re
from app.interfaces.contact_validator_interface import IContactValidator

class ContactValidator(IContactValidator):
    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    WHATSAPP_REGEX = re.compile(r"^\+[1-9]\d{7,14}$")

    def is_valid_email(self, email) -> bool:
        if not email:
            return False
        return bool(self.EMAIL_REGEX.match(email))

    def normalize_whatsapp(self, numero) -> str:
        if not numero:
            return None
        numero_propre = re.sub(r"[\s\-\(\)]", "", numero)

        # Heuristique : un numéro camerounais local (9 chiffres, commence par
        # 6 ou 2) sans indicatif -> on ajoute +237. Best-effort, pas garanti
        # à 100% pour tous les formats possibles.
        if re.match(r"^[62]\d{8}$", numero_propre):
            return "+237" + numero_propre
        if numero_propre.startswith("237") and not numero_propre.startswith("+"):
            return "+" + numero_propre

        return numero_propre

    def is_valid_whatsapp(self, numero) -> bool:
        numero_normalise = self.normalize_whatsapp(numero)
        if not numero_normalise:
            return False
        return bool(self.WHATSAPP_REGEX.match(numero_normalise))

    def validate_prospect_contact(self, company_name, email, whatsapp_number):
        if not company_name:
            return "Le nom de l'entreprise est obligatoire"

        email_ok = email and self.is_valid_email(email)
        whatsapp_ok = whatsapp_number and self.is_valid_whatsapp(whatsapp_number)

        if not email_ok and not whatsapp_ok:
            return "Aucun canal de contact valide (email ou WhatsApp requis)"

        return None