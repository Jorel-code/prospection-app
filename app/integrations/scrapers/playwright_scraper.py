from playwright.sync_api import sync_playwright
from app.interfaces.scraper_engine_interface import IScraperEngine
from app.integrations.scrapers.dto import ScrapedProspect

class PlaywrightScraper(IScraperEngine):
    def scrape(self, sector: str, location: str, keywords: str = None) -> list:
        resultats = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (compatible; ProspectionBot/1.0)"
            )
            page = context.new_page()

            url = self._build_search_url(sector, location, keywords)
            page.goto(url, timeout=30000)
            page.wait_for_selector("div.business-card", timeout=15000)

            self._scroll_to_bottom(page)

            cartes = page.query_selector_all("div.business-card")
            for carte in cartes:
                resultats.append(self._extract_card(carte))

            browser.close()
        return resultats

    def _build_search_url(self, sector, location, keywords):
        base = "https://exemple-source.com/recherche"
        return f"{base}?secteur={sector}&ville={location}&q={keywords or ''}"

    def _scroll_to_bottom(self, page, max_scrolls=10):
        for _ in range(max_scrolls):
            avant = page.evaluate("document.body.scrollHeight")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1200)
            if page.evaluate("document.body.scrollHeight") == avant:
                break

    def _extract_card(self, carte) -> ScrapedProspect:
        nom = carte.query_selector("h3.name")
        tel = carte.query_selector("span.phone")
        site = carte.query_selector("a.website")
        return ScrapedProspect(
            company_name=nom.inner_text().strip() if nom else None,
            whatsapp_number=tel.inner_text().strip() if tel else None,
            facebook_url=site.get_attribute("href") if site else None
        )