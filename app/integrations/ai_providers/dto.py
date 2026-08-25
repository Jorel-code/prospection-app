from dataclasses import dataclass

@dataclass
class GeneratedMessage:
    content: str
    provider_used: str
    channel: str