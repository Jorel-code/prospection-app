from datetime import datetime
from app.extensions import db
from app.models.scraping_job import ScrapingJob
from app.models.prospect import Prospect

class ScrapingService:
    def __init__(self, scraper_engine, contact_validator, prospect_repository):
        self.scraper_engine = scraper_engine          # IScraperEngine
        self.contact_validator = contact_validator      # IContactValidator
        self.prospect_repository = prospect_repository  # IProspectRepository

        def launch(self, user_id, sector, location, keywords=None):
            job = ScrapingJob(
            user_id=user_id, sector=sector, location=location,
            keywords=keywords, engine_used=type(self.scraper_engine).__name__,
            status="running"
        )
        db.session.add(job)
        db.session.commit()

        try:
            scraped_prospects = self.scraper_engine.scrape(sector, location, keywords)

            # Idempotence : on récupère les noms déjà connus pour cet utilisateur,
            # pour ne jamais réinsérer deux fois la même entreprise scrapée.
            noms_existants = {
                p.company_name.strip().lower()
                for p in Prospect.query.filter_by(user_id=user_id).all()
            }

            importes, rejetes, doublons = 0, 0, 0
            for donnee in scraped_prospects:
                nom_normalise = (donnee.company_name or "").strip().lower()

                if nom_normalise in noms_existants:
                    doublons += 1
                    continue
                noms_existants.add(nom_normalise)

                whatsapp_normalise = self.contact_validator.normalize_whatsapp(donnee.whatsapp_number)
                erreur = self.contact_validator.validate_prospect_contact(
                    donnee.company_name, donnee.email, whatsapp_normalise
                )

                prospect = Prospect(
                    user_id=user_id, scraping_job_id=job.id,
                    company_name=donnee.company_name, facebook_url=donnee.facebook_url,
                    whatsapp_number=whatsapp_normalise, email=donnee.email,
                    source="scraping", status="invalid" if erreur else "verified"
                )

                if erreur:
                    rejetes += 1
                else:
                    importes += 1

                self.prospect_repository.save(prospect)

            job.status = "done"
            job.results_count = importes
            job.finished_at = datetime.utcnow()
            db.session.commit()

            return {"job_id": job.id, "trouves": len(scraped_prospects), "importes": importes, "rejetes": rejetes, "doublons": doublons}

        except Exception as e:
            job.status = "failed"
            job.finished_at = datetime.utcnow()
            db.session.commit()
            raise e