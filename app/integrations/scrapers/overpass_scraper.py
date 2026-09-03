import re
import time
import random
import logging
import unicodedata
import requests
from bs4 import BeautifulSoup
from app.interfaces.scraper_engine_interface import IScraperEngine
from app.integrations.scrapers.dto import ScrapedProspect

logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_REGEX = re.compile(r"\+?\d[\d\s\-\(\)]{7,}\d")
CHEMINS_CONTACT = ["", "/contact", "/contact-us", "/contactez-nous", "/a-propos", "/about"]


def _normaliser_texte(texte):
    """Retire accents/casse pour un matching tolérant ('Informatique', 'informatiques', 'Café' -> comparables)."""
    if not texte:
        return ""
    texte = texte.strip().lower()
    texte = unicodedata.normalize("NFD", texte)
    return "".join(c for c in texte if unicodedata.category(c) != "Mn")


class OverpassScraper(IScraperEngine):
    """
    Étage 1 : interroge OpenStreetMap (Overpass API) pour des entreprises réelles.
    Étage 2 : si aucun site web connu, cherche le site officiel via DuckDuckGo HTML.
    Étage 3 : visite le site trouvé pour en extraire l'email/téléphone publiés.
    """

    HEADERS = {"User-Agent": "ProspectionAppBot/1.0 (Projet academique; contact: tonemail@exemple.com)"}

    URLS_OVERPASS = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
    ]

    # Mapping élargi : chaque secteur a plusieurs synonymes/variantes possibles.
    # Toutes les clés sont déjà normalisées (sans accent, en minuscule).
    MAPPING_SECTEURS = {
        "informatique": ['shop="computer"', 'shop="electronics"', 'office="it"'],
        "info": ['shop="computer"', 'shop="electronics"', 'office="it"'],
        "tech": ['shop="computer"', 'shop="electronics"', 'office="it"'],
        "numerique": ['shop="computer"', 'shop="electronics"', 'office="it"'],

        "restauration": ['amenity="restaurant"', 'amenity="cafe"', 'amenity="fast_food"'],
        "restaurant": ['amenity="restaurant"', 'amenity="cafe"', 'amenity="fast_food"'],
        "alimentation": ['shop="supermarket"', 'shop="grocery"', 'shop="convenience"'],
        "hotellerie": ['tourism="hotel"', 'tourism="guest_house"'],
        "hotel": ['tourism="hotel"', 'tourism="guest_house"'],

        "sante": ['amenity="pharmacy"', 'amenity="clinic"', 'amenity="hospital"'],
        "medical": ['amenity="pharmacy"', 'amenity="clinic"', 'amenity="hospital"'],
        "pharmacie": ['amenity="pharmacy"'],

        "finance": ['amenity="bank"', 'office="financial"', 'office="insurance"'],
        "banque": ['amenity="bank"'],
        "assurance": ['office="insurance"'],

        "btp": ['shop="hardware"', 'craft="builder"', 'office="construction"'],
        "construction": ['shop="hardware"', 'craft="builder"', 'office="construction"'],
        "batiment": ['shop="hardware"', 'craft="builder"', 'office="construction"'],

        "education": ['amenity="school"', 'amenity="university"', 'amenity="college"'],
        "ecole": ['amenity="school"'],
        "universite": ['amenity="university"'],

        "commerce": ['shop="clothes"', 'shop="general"', 'shop="department_store"'],
        "mode": ['shop="clothes"', 'shop="shoes"', 'shop="boutique"'],
        "textile": ['shop="clothes"', 'shop="fabric"'],

        "automobile": ['shop="car"', 'shop="car_repair"', 'shop="car_parts"'],
        "auto": ['shop="car"', 'shop="car_repair"', 'shop="car_parts"'],

        "immobilier": ['office="estate_agent"'],

        "agriculture": ['shop="farm"', 'shop="agrarian"'],

        "transport": ['amenity="taxi"', 'shop="car_rental"', 'office="logistics"'],
        "logistique": ['office="logistics"', 'shop="car_rental"'],

        "beaute": ['shop="hairdresser"', 'shop="beauty"', 'shop="cosmetics"'],
        "coiffure": ['shop="hairdresser"'],

        "artisanat": ['craft="carpenter"', 'craft="tailor"', 'shop="craft"'],
    }

    def scrape(self, sector: str, location: str, keywords: str = None) -> list:
        entreprises_osm = self._interroger_overpass(sector, location) or []

        resultats = []
        for entreprise in entreprises_osm:
            site_web = entreprise.get("website")

            if not site_web:
                site_web = self._chercher_site_web_duckduckgo(entreprise["nom"], location)
                time.sleep(random.uniform(1.5, 3))

            email, telephone_enrichi = None, None
            if site_web:
                email, telephone_enrichi = self._extraire_contact_site(site_web)
                time.sleep(random.uniform(1, 2))

            resultats.append(ScrapedProspect(
                company_name=entreprise["nom"],
                email=email,
                whatsapp_number=entreprise.get("telephone") or telephone_enrichi,
                facebook_url=site_web
            ))

        return resultats

    # ------------------------------------------------------------------
    # Étage 1 : OpenStreetMap Overpass API
    # ------------------------------------------------------------------
    def _trouver_filtres_secteur(self, sector):
        """Cherche une correspondance tolérante (accents/casse/sous-chaîne)
        avant de retomber sur une recherche générique."""
        secteur_normalise = _normaliser_texte(sector)
        if not secteur_normalise:
            return None, "aucun secteur renseigné"

        # 1. Correspondance exacte
        if secteur_normalise in self.MAPPING_SECTEURS:
            return self.MAPPING_SECTEURS[secteur_normalise], f"correspondance exacte '{secteur_normalise}'"

        # 2. Correspondance partielle (le mot tapé contient une clé connue, ou l'inverse)
        for cle, filtres in self.MAPPING_SECTEURS.items():
            if cle in secteur_normalise or secteur_normalise in cle:
                return filtres, f"correspondance partielle '{secteur_normalise}' ~ '{cle}'"

        return None, f"'{secteur_normalise}' non reconnu"

    def _geocoder_location(self, location):
        try:
            response = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": location, "format": "json", "limit": 1},
                headers=self.HEADERS,
                timeout=15
            )
            resultats = response.json()
            if not resultats:
                logger.warning(f"Nominatim: aucun résultat pour '{location}'")
                return None
            lat, lon = float(resultats[0]["lat"]), float(resultats[0]["lon"])
            logger.info(f"'{location}' géocodé -> lat={lat}, lon={lon}")
            return lat, lon
        except Exception as e:
            logger.error(f"Erreur géocodage pour '{location}': {e}", exc_info=True)
            return None

    def _interroger_overpass(self, sector, location):
        coords = self._geocoder_location(location)
        if not coords:
            return []
        lat, lon = coords

        filtres, raison = self._trouver_filtres_secteur(sector)

        if filtres:
            clauses = "\n".join(f'  node[{f}](around:15000,{lat},{lon});' for f in filtres)
            logger.info(f"Secteur '{sector}' -> {raison} -> {len(filtres)} filtre(s) ciblé(s)")
        else:
            # Recherche générale élargie : mieux qu'un simple shop+office pour
            # maximiser les chances de trouver quelque chose de pertinent
            # même sur un secteur totalement inconnu du mapping.
            clauses = f"""  node["shop"](around:15000,{lat},{lon});
  node["office"](around:15000,{lat},{lon});
  node["craft"](around:15000,{lat},{lon});"""
            logger.warning(f"Secteur '{sector}' -> {raison} -> recherche générale élargie (shop+office+craft)")

        requete = f"""
        [out:json][timeout:60];
        (
{clauses}
        );
        out body 40;
        """

        for url in self.URLS_OVERPASS:
            try:
                response = requests.post(url, data={"data": requete}, headers=self.HEADERS, timeout=70)
                logger.info(f"{url} -> status_code={response.status_code}")

                if response.status_code != 200:
                    continue

                data = response.json()
                elements = data.get("elements", [])
                logger.info(f"{len(elements)} éléments bruts reçus depuis {url}")

                if elements:
                    return self._parser_elements(elements)

            except Exception as e:
                logger.error(f"Erreur sur {url} : {e}", exc_info=True)
                continue

        logger.error("Tous les serveurs Overpass ont échoué.")
        return []

    def _parser_elements(self, elements):
        entreprises = []
        for element in elements:
            tags = element.get("tags", {})
            nom = tags.get("name")
            if not nom:
                continue
            entreprises.append({
                "nom": nom,
                "telephone": tags.get("phone") or tags.get("contact:phone"),
                "website": tags.get("website") or tags.get("contact:website"),
                "adresse": tags.get("addr:full") or tags.get("addr:street"),
            })
        return entreprises

    # ------------------------------------------------------------------
    # Étage 2 : recherche du site officiel via DuckDuckGo (usage raisonnable)
    # ------------------------------------------------------------------
    def _chercher_site_web_duckduckgo(self, nom_entreprise, location):
        try:
            params = {"q": f"{nom_entreprise} {location} site officiel"}
            response = requests.get(
                "https://html.duckduckgo.com/html/",
                params=params, headers=self.HEADERS, timeout=10
            )
            soup = BeautifulSoup(response.text, "lxml")
            premier_lien = soup.select_one("a.result__a")
            if premier_lien and premier_lien.get("href"):
                return premier_lien["href"]
        except Exception as e:
            logger.warning(f"DuckDuckGo échec pour '{nom_entreprise}': {e}")
        return None

    # ------------------------------------------------------------------
    # Étage 3 : extraction email/téléphone depuis le site de l'entreprise
    # ------------------------------------------------------------------
    def _extraire_contact_site(self, url):
        base = url.rstrip("/")
        for chemin in CHEMINS_CONTACT:
            try:
                response = requests.get(base + chemin, headers=self.HEADERS, timeout=8)
                if response.status_code != 200:
                    continue

                texte = BeautifulSoup(response.text, "lxml").get_text(" ", strip=True)
                email_trouve = EMAIL_REGEX.search(texte)
                telephone_trouve = PHONE_REGEX.search(texte)

                if email_trouve:
                    return email_trouve.group(0), (telephone_trouve.group(0) if telephone_trouve else None)
            except Exception:
                continue
        return None, None