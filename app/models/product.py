from app.forms.extensions import db

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.Text, nullable=True)
    demo_link = db.Column(db.String(500), nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    # Remarque : la contrainte unique sur "email" a été retirée ici, ce champ
    # n'existe pas sur Product (c'était une copie du modèle Prospect par erreur).

