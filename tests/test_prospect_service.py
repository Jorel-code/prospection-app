import pytest
from app.repositories.sqlalchemy_prospect_repository import SQLAlchemyProspectRepository
from app.validators.contact_validator import ContactValidator
from app.services.prospect_service import ProspectService
from app.models.user import User
from app.extensions import db


@pytest.fixture()
def prospect_service(app):
    user = User(username="test", email="test@test.com", password_hash="x")
    db.session.add(user)
    db.session.commit()

    service = ProspectService(
        prospect_repository=SQLAlchemyProspectRepository(),
        contact_validator=ContactValidator()
    )
    return service, user.id


def test_create_prospect_valide(app, prospect_service):
    service, user_id = prospect_service
    prospect = service.create(user_id=user_id, company_name="ACME", email="contact@acme.com")
    assert prospect.id is not None
    assert prospect.status == "verified"


def test_create_prospect_sans_contact_leve_erreur(app, prospect_service):
    service, user_id = prospect_service
    with pytest.raises(ValueError):
        service.create(user_id=user_id, company_name="ACME")


def test_create_prospect_email_duplique_leve_erreur_claire(app, prospect_service):
    service, user_id = prospect_service
    service.create(user_id=user_id, company_name="ACME", email="contact@acme.com")
    with pytest.raises(ValueError, match="existe déjà"):
        service.create(user_id=user_id, company_name="AUTRE", email="contact@acme.com")


def test_create_bulk_isole_les_erreurs(app, prospect_service):
    service, user_id = prospect_service
    lignes = [
        {"company_name": "A", "email": "a@a.com"},
        {"company_name": ""},
        {"company_name": "C", "email": "c@c.com"},
    ]
    resultats = service.create_bulk(user_id=user_id, lignes=lignes)
    assert resultats["crees"] == 2
    assert len(resultats["erreurs"]) == 1