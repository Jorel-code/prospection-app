from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from app.extensions import db

ph = PasswordHasher()

class AuthService:
    def register(self, username, email, password):
        from app.models.user import User

        if not username or not email or not password:
            raise ValueError("username, email et password sont obligatoires")

        if User.query.filter_by(email=email).first():
            raise ValueError("Un compte existe déjà avec cet email")

        user = User(
            username=username,
            email=email,
            password_hash=ph.hash(password)
        )
        db.session.add(user)
        db.session.commit()
        return user

    def authenticate(self, email, password):
        from app.models.user import User

        user = User.query.filter_by(email=email).first()
        if not user:
            raise ValueError("Identifiants invalides")

        try:
            ph.verify(user.password_hash, password)
        except VerifyMismatchError:
            raise ValueError("Identifiants invalides")

        return user