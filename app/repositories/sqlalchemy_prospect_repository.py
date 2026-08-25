from app.interfaces.prospect_repository_interface import IProspectRepository
from app.extensions import db

class SQLAlchemyProspectRepository(IProspectRepository):
    def save(self, prospect):
        db.session.add(prospect)
        db.session.commit()
        return prospect

    def find_all(self, user_id):
        from app.models.prospect import Prospect
        return Prospect.query.filter_by(user_id=user_id).all()

    def find_by_id(self, prospect_id):
        from app.models.prospect import Prospect
        return Prospect.query.get(prospect_id)