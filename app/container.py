from app.repositories.sqlalchemy_prospect_repository import SQLAlchemyProspectRepository
from app.validators.contact_validator import ContactValidator
from app.services.prospect_service import ProspectService

prospect_repository = SQLAlchemyProspectRepository()
contact_validator = ContactValidator()

def get_prospect_service():
    return ProspectService(
        prospect_repository=prospect_repository,
        contact_validator=contact_validator
    )