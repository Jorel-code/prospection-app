import pytest
from types import SimpleNamespace
from app.services.campaign_service import CampaignService
from app.services.rate_limiter import RateLimiter
from app.repositories.sqlalchemy_prospect_repository import SQLAlchemyProspectRepository
from app.models.user import User
from app.models.prospect import Prospect
from app.models.product import Product
from app.extensions import db


class FakeAIGenerationService:
    def generate_message(self, prospect_id, product_id, channel):
        return SimpleNamespace(content="Message généré", provider_used="fake")


class FakeChannelSender:
    def __init__(self):
        self.envois = []

    def send(self, destinataire, message):
        self.envois.append(destinataire)
        return {"statut": "envoye"}


@pytest.fixture()
def setup(app):
    user = User(username="t", email="t@t.com", password_hash="x")
    db.session.add(user)
    db.session.commit()

    product = Product(user_id=user.id, name="Produit Test")
    db.session.add(product)

    p1 = Prospect(user_id=user.id, company_name="A", email="a@a.com", source="manual", status="verified")
    p2 = Prospect(user_id=user.id, company_name="B", email="b@b.com", source="manual", status="verified")
    db.session.add_all([p1, p2])
    db.session.commit()

    return user, product, p1, p2


def test_launch_campaign_envoie_a_tous_les_prospects(app, setup):
    user, product, p1, p2 = setup
    service = CampaignService(
        channel_sender=FakeChannelSender(),
        ai_generation_service=FakeAIGenerationService(),
        prospect_repository=SQLAlchemyProspectRepository(),
        rate_limiter=RateLimiter(max_appels=100, periode_secondes=60)
    )
    resultat = service.launch(user_id=user.id, product_id=product.id,
                               prospect_ids=[p1.id, p2.id], channel="email", name="Test")

    assert resultat["envoyes"] == 2
    assert resultat["echecs"] == 0

    from app.models.campaign import Campaign
    assert Campaign.query.get(resultat["campaign_id"]).status == "completed"


def test_launch_campaign_resiste_a_un_prospect_introuvable(app, setup):
    user, product, p1, p2 = setup
    service = CampaignService(
        channel_sender=FakeChannelSender(),
        ai_generation_service=FakeAIGenerationService(),
        prospect_repository=SQLAlchemyProspectRepository(),
        rate_limiter=RateLimiter(max_appels=100, periode_secondes=60)
    )
    resultat = service.launch(user_id=user.id, product_id=product.id,
                               prospect_ids=[999, p2.id], channel="email", name="Test")

    assert resultat["envoyes"] == 1
    assert resultat["echecs"] == 1

    from app.models.campaign import Campaign
    assert Campaign.query.get(resultat["campaign_id"]).status == "completed"