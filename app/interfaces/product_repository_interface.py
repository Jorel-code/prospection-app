from abc import ABC, abstractmethod

class IProductRepository(ABC):
    @abstractmethod
    def save(self, product): ...

    @abstractmethod
    def find_all(self, user_id): ...

    @abstractmethod
    def find_by_id(self, product_id): ...