# NOTE PEDAGOGIQUE : ce module correspond au Guide 2 (catalogue produit),
# que vous n'avez pas encore suivi selon votre programme. Il est laissé ici
# à l'état de brouillon corrigé au niveau syntaxe uniquement, pour que le
# projet reste important et n'empêche pas les autres modules de fonctionner.
# Les imports manquants (Product, ProductRepository) devront être ajoutés
# et la logique complétée quand vous traiterez le module produit.

# from app.models.product import Product
# from app.interfaces.product_repository_interface import ProductRepository


class AjouterProduct:
    def __init__(self, repository):
        self.repository = repository

    def execute(self, nom, description, images, lien_demo):
        # TODO (Guide 2) : construire l'entité Product puis la sauvegarder
        raise NotImplementedError("Module produit pas encore implémenté (voir Guide 2).")


class AfficherProduct:
    def __init__(self, repository):
        self.repository = repository

    def get_all(self):
        raise NotImplementedError("Module produit pas encore implémenté (voir Guide 2).")

    def get_by_name(self, nom):
        raise NotImplementedError("Module produit pas encore implémenté (voir Guide 2).")
