from app.models.prospect import Prospect

class ProspectService:
    def __init__(self, prospect_repository):
        self.prospect_repository = prospect_repository  # IProspectRepository

    def create(self, user_id, company_name, email=None, whatsapp_number=None, notes=None, source="manual"):
        # Validation métier : on préfère lever une erreur claire ici plutôt que
        # de laisser SQLite renvoyer une IntegrityError brute (500 illisible).
        if not company_name or not company_name.strip():
            raise ValueError("Le champ 'company_name' est obligatoire et ne peut pas être vide.")
        if not email and not whatsapp_number:
            raise ValueError("Le prospect doit avoir au moins un email ou un numéro WhatsApp.")

        prospect = Prospect(
            user_id=user_id,
            company_name=company_name,
            email=email,
            whatsapp_number=whatsapp_number,
            notes=notes,
            source=source,
            status="raw"
        )
        return self.prospect_repository.save(prospect)
