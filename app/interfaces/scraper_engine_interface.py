from abc import ABC, abstractmethod

class IScraperEngine(ABC):
    @abstractmethod
    def scrape(self, sector: str, location: str, keywords: str = None) -> list:
        """Retourne une liste de ScrapedProspect"""
        ...