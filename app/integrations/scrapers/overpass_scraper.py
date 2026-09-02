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

    def scrape(self, sector: str, location: str, keywords: str = None) -> list:
        entreprises_osm = self._interroger_overpass(sector, location)

        resultats = []
        for entreprise in entreprises_osm:
            site_web = entreprise.get("website")

            if not site_web:
                site_web = self._chercher_site_web_duckduckgo(entreprise["nom"], location)
                time.sleep(random.uniform(1.5, 3))  # respect du site interrogé

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
    def _interroger_overpass(self, sector, location):
        requete = f"""
        [out:json][timeout:25];
        area["name"~"{location}",i]->.zone;
        (
          node["shop"](area.zone);
          node["office"](area.zone);
          node["amenity"="restaurant"](area.zone);
        );
        out body 100;
        """
        try:
            response = requests.post(
                "https://overpass-api.de/api/interpreter",
                data={"data": requete},
                headers=self.HEADERS,
                timeout=30
            )
            data = response.json()
        except Exception:
            return []

        entreprises = []
        for element in data.get("elements", []):
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
        except Exception:
            pass
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