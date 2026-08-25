def build_prompt(prospect, product, channel):
    system_prompt = """Tu es un commercial expérimenté et empathique, expert en
prospection B2B. Tu écris des messages courts, directs, jamais génériques, qui
donnent l'impression d'avoir été écrits spécifiquement pour le destinataire.
Tu ne dois JAMAIS inventer d'information qui ne serait pas fournie dans le contexte."""

    contraintes_canal = {
        "email": "Structure: objet suggéré + corps de 3-4 phrases, vouvoiement, ton professionnel.",
        "whatsapp": "Style conversationnel et court (2-3 phrases max), plus direct."
    }

    user_prompt = f"""INFORMATIONS SUR LE PROSPECT :
- Entreprise : {prospect.company_name}
- Notes de prospection : {prospect.notes or "Aucune note spécifique disponible"}

PRODUIT À PROMOUVOIR :
- Nom : {product.name}
- Description : {product.description}
- Lien de démonstration : {product.demo_link}

CANAL DE DESTINATION : {channel}
CONTRAINTES SPÉCIFIQUES : {contraintes_canal.get(channel, "")}

CONSIGNE : Génère UNIQUEMENT le message final, sans commentaire ni explication
avant ou après. Le message doit se terminer par une question ouverte."""

    return system_prompt, user_prompt


def clean_generated_message(texte_brut):
    texte = texte_brut.strip()
    for prefixe in ["Voici le message :", "Message :", "Voici votre message :"]:
        if texte.startswith(prefixe):
            texte = texte[len(prefixe):].strip()
    if texte.startswith('"') and texte.endswith('"'):
        texte = texte[1:-1]
    return texte.strip()


class AIGenerationService:
    def __init__(self, ai_provider, prospect_repository, product_repository):
        self.ai_provider = ai_provider                 # IAIMessageGenerator (FallbackAIClient)
        self.prospect_repository = prospect_repository  # IProspectRepository
        self.product_repository = product_repository    # IProductRepository

    def generate_message(self, prospect_id, product_id, channel):
        prospect = self.prospect_repository.find_by_id(prospect_id)
        product = self.product_repository.find_by_id(product_id)

        if not prospect or not product:
            raise ValueError("Prospect ou produit introuvable")
        if channel not in ("email", "whatsapp"):
            raise ValueError("Canal invalide : doit être 'email' ou 'whatsapp'")

        system_prompt, user_prompt = build_prompt(prospect, product, channel)
        generated = self.ai_provider.generate(system_prompt, user_prompt, channel)
        generated.content = clean_generated_message(generated.content)

        return generated