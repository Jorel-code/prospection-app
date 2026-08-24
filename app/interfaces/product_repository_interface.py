from abc import ABC, abstractmethod

class ProductRepository(ABC):
    @abstractmethod
    def save(self, product): ...

    @abstractmethod
    def find_all(self): ...
    
    @abstractmethod
    def find_by_name(self, product_name): ...