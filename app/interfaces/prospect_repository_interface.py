from abc import ABC, abstractmethod

class IProspectRepository(ABC):
    @abstractmethod
    def save(self, prospect): ...

    @abstractmethod
    def find_all(self, user_id): ...

    @abstractmethod
    def find_by_id(self, prospect_id): ...
