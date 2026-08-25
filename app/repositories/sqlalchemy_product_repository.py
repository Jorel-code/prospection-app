from app.interfaces.product_repository_interface import IProductRepository
from app.extensions import db

class SQLAlchemyProductRepository(IProductRepository):
    def save(self, product):
        db.session.add(product)
        db.session.commit()
        return product

    def find_all(self, user_id):
        from app.models.product import Product
        return Product.query.filter_by(user_id=user_id).all()

    def find_by_id(self, product_id):
        from app.models.product import Product
        return Product.query.get(product_id)