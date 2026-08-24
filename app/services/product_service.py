class AjouterProduct:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def execute(self, nom, description, images, lien_demo):
        product = Product(nom=nom, description=description, images=images, lien_demo=lien_demo)
        return self.repository.save(product)

class AfficherProduct:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def get_all():
        return self.repository.find_all()

    def get_by_name(nom):
        product = Product(nom=nom, description=description, images=images, lien_demo=lien_demo)
        return self.repository.find_by_name(product_nom)
         