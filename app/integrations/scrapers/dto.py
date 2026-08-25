from dataclasses import dataclass
from typing import Optional

@dataclass
class ScrapedProspect:
    company_name: str
    facebook_url: Optional[str] = None
    whatsapp_number: Optional[str] = None
    email: Optional[str] = None