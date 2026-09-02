from app.interfaces.scraper_engine_interface import IScraperEngine


class FallbackScraper(IScraperEngine):
    """Essaie plusieurs moteurs de scraping dans l'ordre, en cas d'échec ou
    d'indisponibilité de l'un d'eux. Même principe que FallbackAIClient
    pour les fournisseurs IA (Guide 4)."""

    def __init__(self, scrapers: list):
        self.scrapers = scrapers

    def scrape(self, sector, location, keywords=None):
        derniere_erreur = None
        for scraper in self.scrapers:
            nom = type(scraper).__name__
            try:
                print(f"[FallbackScraper] Tentative avec {nom}...")
                resultats = scraper.scrape(sector, location, keywords)
                if resultats:
                    print(f"[FallbackScraper] {nom} a réussi : {len(resultats)} résultat(s).")
                    return resultats
                print(f"[FallbackScraper] {nom} n'a rien retourné, on tente le suivant.")
            except Exception as e:
                derniere_erreur = e
                print(f"[FallbackScraper] {nom} a échoué : {e}")
                continue

        if derniere_erreur:
            raise Exception(f"Tous les scrapers ont échoué. Dernière erreur : {derniere_erreur}")
        return []