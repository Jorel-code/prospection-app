from app.repositories.sqlalchemy_prospect_repository import SQLAlchemyProspectRepository
from app.validators.contact_validator import ContactValidator
from app.services.prospect_service import ProspectService
from app.repositories.sqlalchemy_product_repository import SQLAlchemyProductRepository
from app.services.product_service import ProductService
from app.integrations.scrapers.playwright_scraper import PlaywrightScraper
from app.integrations.scrapers.bs4_scraper import BS4Scraper
from app.integrations.scrapers.overpass_scraper import OverpassScraper
from app.integrations.scrapers.fallback_scraper import FallbackScraper

from app.services.scraping_service import ScrapingService
from app.integrations.ai_providers.groq_provider import GroqProvider
from app.integrations.ai_providers.gemini_provider import GeminiProvider
from app.integrations.ai_providers.fallback_ai_client import FallbackAIClient
from app.services.ai_generation_service import AIGenerationService
from app.integrations.channels.email_sender import EmailSender
from app.integrations.channels.whatsapp_sender import WhatsAppSender
from app.services.campaign_service import CampaignService
from app.services.rate_limiter import RateLimiter
from app.services.auth_service import AuthService


prospect_repository = SQLAlchemyProspectRepository()
contact_validator = ContactValidator()
product_repository = SQLAlchemyProductRepository()
scraper_engine = FallbackScraper(scrapers=[OverpassScraper(), BS4Scraper()])
ai_provider = FallbackAIClient(providers=[GroqProvider(), GeminiProvider()])
email_sender = EmailSender()
whatsapp_sender = WhatsAppSender()
rate_limiter = RateLimiter(max_appels=10, periode_secondes=60)

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

def get_ai_generation_service():
    return AIGenerationService(
        ai_provider=ai_provider,
        prospect_repository=prospect_repository,  # déjà défini
        product_repository=product_repository      # déjà défini
    )

def get_campaign_service(channel="email"):
    return CampaignService(
        channel_sender=get_channel_sender(channel),
        ai_generation_service=get_ai_generation_service(),
        prospect_repository=prospect_repository,
        rate_limiter=rate_limiter
    )

def get_channel_sender(channel):
    return whatsapp_sender if channel == "whatsapp" else email_sender

def get_auth_service():
    return AuthService()
