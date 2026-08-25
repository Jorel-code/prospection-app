from abc import ABC, abstractmethod

class IContactValidator(ABC):
    @abstractmethod
    def is_valid_email(self, email) -> bool: ...

    @abstractmethod
    def is_valid_whatsapp(self, numero) -> bool: ...

    @abstractmethod
    def normalize_whatsapp(self, numero) -> str: ...
