class ProspectService:
    def __init__(self, prospect_repository, contact_validator):
        self.prospect_repository = prospect_repository   # IProspectRepository
        self.contact_validator = contact_validator         # IContactValidator

    def create(self, user_id, company_name, email=None, whatsapp_number=None, notes=None, source="manual"):
        whatsapp_normalise = self.contact_validator.normalize_whatsapp(whatsapp_number)
        erreur = self.contact_validator.validate_prospect_contact(company_name, email, whatsapp_normalise)
        if erreur:
            raise ValueError(erreur)

        from app.models.prospect import Prospect
        prospect = Prospect(
            user_id=user_id,
            company_name=company_name,
            email=email,
            whatsapp_number=whatsapp_normalise,
            notes=notes,
            source=source,
            status="verified"
        )
        return self.prospect_repository.save(prospect)

    def create_bulk(self, user_id, lignes, source="manual"):
        resultats = {"crees": 0, "erreurs": []}
        for i, ligne in enumerate(lignes):
            try:
                self.create(
                    user_id=user_id,
                    company_name=ligne.get("company_name"),
                    email=ligne.get("email"),
                    whatsapp_number=ligne.get("whatsapp_number"),
                    notes=ligne.get("notes"),
                    source=source
                )
                resultats["crees"] += 1
            except ValueError as e:
                resultats["erreurs"].append({"ligne": i, "erreur": str(e)})
        return resultats

    def import_csv(self, user_id, fichier_csv):
        import pandas as pd

        df = pd.read_csv(fichier_csv)
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

        resultats = {"total": len(df), "importes": 0, "rejetes": 0, "doublons": 0, "erreurs": []}
        emails_vus = set()

        for index, ligne in df.iterrows():
            company_name = str(ligne.get("company_name", "")).strip()
            email = str(ligne.get("email", "")).strip() if pd.notna(ligne.get("email")) else None
            whatsapp_number = str(ligne.get("whatsapp_number", "")).strip() if pd.notna(ligne.get("whatsapp_number")) else None

            email_normalise = (email or "").strip().lower()
            if email_normalise and email_normalise in emails_vus:
                resultats["doublons"] += 1
                continue
            if email_normalise:
                emails_vus.add(email_normalise)

            try:
                self.create(user_id=user_id, company_name=company_name, email=email,
                            whatsapp_number=whatsapp_number, source="csv")
                resultats["importes"] += 1
            except ValueError as e:
                resultats["rejetes"] += 1
                resultats["erreurs"].append({"ligne": index + 2, "erreur": str(e)})

        return resultats