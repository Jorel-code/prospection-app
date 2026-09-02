from datetime import datetime
from app.extensions import db

class CampaignService:
    def __init__(self, channel_sender, ai_generation_service, prospect_repository, rate_limiter):
        self.channel_sender = channel_sender                 # IChannelSender
        self.ai_generation_service = ai_generation_service     # AIGenerationService
        self.prospect_repository = prospect_repository         # IProspectRepository
        self.rate_limiter = rate_limiter

    def launch(self, user_id, product_id, prospect_ids, channel, name):
        from app.models.campaign import Campaign
        from app.models.campaign_message import CampaignMessage

        campaign = Campaign(
            user_id=user_id, product_id=product_id,
            name=name, channel=channel, status="running"
        )
        db.session.add(campaign)
        db.session.commit()

        envoyes, echecs = 0, 0
        prospect_ids_traites = set()  # évite les doublons si la même liste contient 2x le même id

        for prospect_id in prospect_ids:
            if prospect_id in prospect_ids_traites:
                continue
            prospect_ids_traites.add(prospect_id)

            try:
                prospect = self.prospect_repository.find_by_id(prospect_id)
                if not prospect:
                    echecs += 1
                    continue

                generated = self.ai_generation_service.generate_message(prospect_id, product_id, channel)

                campaign_message = CampaignMessage(
                    campaign_id=campaign.id, prospect_id=prospect_id,
                    generated_message=generated.content, channel=channel, status="queued"
                )
                db.session.add(campaign_message)
                db.session.commit()

                self.rate_limiter.wait_if_needed()

                destinataire = prospect.email if channel == "email" else prospect.whatsapp_number
                resultat = self.channel_sender.send(destinataire, generated.content)

                campaign_message.status = "sent" if resultat["statut"] == "envoye" else "failed"
                campaign_message.error_detail = resultat.get("raison")
                campaign_message.sent_at = datetime.utcnow() if resultat["statut"] == "envoye" else None
                db.session.commit()

                if resultat["statut"] == "envoye":
                    envoyes += 1
                else:
                    echecs += 1

            except Exception as e:
                # Une erreur sur UN prospect ne doit jamais faire échouer toute la campagne.
                print(f"[CampaignService] Échec pour prospect_id={prospect_id} : {e}")
                echecs += 1
                db.session.rollback()
                continue

        campaign.status = "completed"
        db.session.commit()

        return {"campaign_id": campaign.id, "envoyes": envoyes, "echecs": echecs}