from app.repositories.sqlalchemy_prospect_repository import SQLAlchemyProspectRepository
from app.validators.contact_validator import ContactValidator
from app.services.prospect_service import ProspectService
from app.repositories.sqlalchemy_product_repository import SQLAlchemyProductRepository
from app.services.product_service import ProductService
from app.integrations.scrapers.playwright_scraper import PlaywrightScraper
from app.services.scraping_service import ScrapingService

prospect_repository = SQLAlchemyProspectRepository()
contact_validator = ContactValidator()
product_repository = SQLAlchemyProductRepository()
scraper_engine = PlaywrightScraper()

def get_prospect_service():
    return ProspectService(
        prospect_repository=prospect_repository,
        contact_validator=contact_validator
    )

def get_product_service():
    return ProductService(product_repository=product_repository)

def get_scraping_service():
    return ScrapingService(
        scraper_engine=scraper_engine,
        contact_validator=contact_validator,
        prospect_repository=prospect_repository
    )