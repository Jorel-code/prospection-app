import pytest
from app.services.scraping_service import ScrapingService
from app.repositories.sqlalchemy_prospect_repository import SQLAlchemyProspectRepository
from app.validators.contact_validator import ContactValidator
from app.integrations.scrapers.dto import ScrapedProspect
from app.models.user import User
from app.extensions import db


class FakeScraperEngine:
    """Faux moteur de scraping : évite tout appel réseau pendant les tests."""
    def __init__(self, resultats):
        self.resultats = resultats

    def scrape(self, sector, location, keywords=None):
        return self.resultats


class ScraperQuiPlante:
    def scrape(self, sector, location, keywords=None):
        raise Exception("Panne simulée")


@pytest.fixture()
def user(app):
    u = User(username="test", email="test@test.com", password_hash="x")
    db.session.add(u)
    db.session.commit()
    return u


def test_run_job_deduplique_les_entreprises(app, user):
    fake = FakeScraperEngine([
        ScrapedProspect(company_name="ACME"),
        ScrapedProspect(company_name="ACME"),  # doublon exact
        ScrapedProspect(company_name="Beta", email="beta@beta.com"),
    ])
    service = ScrapingService(fake, ContactValidator(), SQLAlchemyProspectRepository())
    job = service.create_job(user_id=user.id, sector="test", location="Douala")
    service.run_job(job.id)

    from app.models.scraping_job import ScrapingJob
    from app.models.prospect import Prospect

    assert ScrapingJob.query.get(job.id).status == "done"
    assert Prospect.query.filter_by(user_id=user.id).count() == 2  # ACME une fois + Beta


def test_run_job_marque_invalid_sans_contact(app, user):
    fake = FakeScraperEngine([ScrapedProspect(company_name="SansContact")])
    service = ScrapingService(fake, ContactValidator(), SQLAlchemyProspectRepository())
    job = service.create_job(user_id=user.id, sector="test", location="Douala")
    service.run_job(job.id)

    from app.models.prospect import Prospect
    p = Prospect.query.filter_by(user_id=user.id, company_name="SansContact").first()
    assert p.status == "invalid"


def test_run_job_echec_scraper_marque_job_failed_sans_planter(app, user):
    service = ScrapingService(ScraperQuiPlante(), ContactValidator(), SQLAlchemyProspectRepository())
    job = service.create_job(user_id=user.id, sector="test", location="Douala")

    service.run_job(job.id)  # ne doit lever aucune exception

    from app.models.scraping_job import ScrapingJob
    job_final = ScrapingJob.query.get(job.id)
    assert job_final.status == "failed"
    assert job_final.error_detail is not None