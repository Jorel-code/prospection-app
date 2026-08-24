from app.interfaces.prospect_repository_interface import IProspectRepository
from app.models.prospect import Prospect
from app.forms.extensions import db

class SQLAlchemyProspectRepository(IProspectRepository):
    def save(self, prospect: Prospect):
        db.session.add(prospect)
        db.session.commit()
        return prospect

    def find_all(self, user_id):
        return Prospect.query.filter_by(user_id=user_id).all()

    def find_by_id(self, prospect_id):
        return Prospect.query.get(prospect_id)
