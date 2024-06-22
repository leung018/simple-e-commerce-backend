from abc import ABC, abstractmethod

from app.models.product import Product


class ProductRepositoryInterface(ABC):
    @abstractmethod
    def save(self, product: Product):
        pass

    @abstractmethod
    def get_by_id(self, product_id: str) -> Product:
        pass
