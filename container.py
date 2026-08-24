from app.repositories.sqlalchemy_prospect_repository import SQLAlchemyProspectRepository
from app.services.prospect_service import ProspectService

# Instanciation des repositories (implémentations concrètes des interfaces)
prospect_repository = SQLAlchemyProspectRepository()

# Instanciation des services, avec injection des repositories
def get_prospect_service():
    return ProspectService(prospect_repository=prospect_repository)
