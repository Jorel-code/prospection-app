import re
import time
import random
import requests
from bs4 import BeautifulSoup
from app.interfaces.scraper_engine_interface import IScraperEngine
from app.integrations.scrapers.dto import ScrapedProspect

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_REGEX = re.compile(r"\+?\d[\d\s\-\(\)]{7,}\d")
CHEMINS_CONTACT = ["", "/contact", "/contact-us", "/contactez-nous", "/a-propos", "/about"]


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
    def _geocoder_location(self, location):
        """Convertit un nom de lieu ('Douala') en coordonnées GPS via Nominatim."""
        try:
            response = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": location, "format": "json", "limit": 1},
                headers=self.HEADERS,
                timeout=15
            )
            resultats = response.json()
            if not resultats:
                print(f"[OverpassScraper] Nominatim: aucun résultat pour '{location}'")
                return None
            lat, lon = float(resultats[0]["lat"]), float(resultats[0]["lon"])
            print(f"[OverpassScraper] '{location}' géocodé -> lat={lat}, lon={lon}")
            return lat, lon
        except Exception as e:
            print(f"[OverpassScraper] ERREUR géocodage : {e}")
            return None

    MAPPING_SECTEURS = {
        "informatique": ['shop="computer"', 'shop="electronics"', 'office="it"'],
        "restauration": ['amenity="restaurant"', 'amenity="cafe"', 'amenity="fast_food"'],
        "sante": ['amenity="pharmacy"', 'amenity="clinic"', 'amenity="hospital"'],
        "finance": ['amenity="bank"', 'office="financial"', 'office="insurance"'],
        "btp": ['shop="hardware"', 'craft="builder"', 'office="construction"'],
        "education": ['amenity="school"', 'amenity="university"', 'amenity="college"'],
    }

    def _interroger_overpass(self, sector, location):
        coords = self._geocoder_location(location)
        if not coords:
            return []
        lat, lon = coords

        secteur_normalise = (sector or "").strip().lower()
        filtres = self.MAPPING_SECTEURS.get(secteur_normalise)

        if filtres:
            clauses = "\n".join(f'  node[{f}](around:15000,{lat},{lon});' for f in filtres)
            print(f"[OverpassScraper] Secteur reconnu '{secteur_normalise}' -> {len(filtres)} filtre(s) ciblé(s)")
        else:
            clauses = f"""  node["shop"](around:15000,{lat},{lon});
  node["office"](around:15000,{lat},{lon});"""
            print(f"[OverpassScraper] Secteur '{secteur_normalise}' non reconnu -> recherche générale (shop+office)")

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
                print(f"[OverpassScraper] {url} -> status_code={response.status_code}")
                if response.status_code != 200:
                    continue
                data = response.json()
                elements = data.get("elements", [])
                print(f"[OverpassScraper] {len(elements)} éléments bruts reçus")
                if elements:
                    return self._parser_elements(elements)
            except Exception as e:
                print(f"[OverpassScraper] ERREUR sur {url} : {e}")
                continue

        print("[OverpassScraper] Tous les serveurs Overpass ont échoué.")
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
            print(f"[OverpassScraper] DuckDuckGo échec pour '{nom_entreprise}': {e}")
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