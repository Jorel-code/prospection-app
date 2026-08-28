import requests
from bs4 import BeautifulSoup
from app.interfaces.scraper_engine_interface import IScraperEngine
from app.integrations.scrapers.dto import ScrapedProspect

class BS4Scraper(IScraperEngine):
    def scrape(self, sector: str, location: str, keywords: str = None) -> list:
        url = "https://fr.wikipedia.org/wiki/Cat%C3%A9gorie:Entreprise_ayant_son_si%C3%A8ge_au_Cameroun"
        headers = {"User-Agent": "ProspectionAppBot/1.0 (Projet academique; contact: tonemail@exemple.com)"}

        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "lxml")

        contenu = soup.select_one("div#mw-pages")
        resultats = []

        if not contenu:
            return resultats

        for lien in contenu.select("li a"):
            company_name = lien.get_text(strip=True)
            if not company_name or len(company_name) > 150:
                continue

            resultats.append(ScrapedProspect(
                company_name=company_name,
                email=None,
                whatsapp_number=None,
                facebook_url=None
            ))

        return resultats