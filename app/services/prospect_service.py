from app.models.prospect import Prospect

class ProspectService:
    def __init__(self, prospect_repository):
        self.prospect_repository = prospect_repository  # IProspectRepository

    def create(self, user_id, company_name, email=None, whatsapp_number=None, notes=None, source="manual"):
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
