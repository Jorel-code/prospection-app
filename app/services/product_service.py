class ProductService:
    def __init__(self, product_repository):
        self.product_repository = product_repository  # IProductRepository

    def create(self, user_id, name, description=None, image_url=None, demo_link=None):
        if not name:
            raise ValueError("Le nom du produit est obligatoire")

        from app.models.product import Product
        product = Product(
            user_id=user_id,
            name=name,
            description=description,
            image_url=image_url,
            demo_link=demo_link
        )
        return self.product_repository.save(product)

    def list_all(self, user_id):
        return self.product_repository.find_all(user_id)

    def get_by_id(self, product_id):
        product = self.product_repository.find_by_id(product_id)
        if not product:
            raise ValueError("Produit introuvable")
        return product