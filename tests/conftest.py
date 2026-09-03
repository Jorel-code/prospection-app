from dotenv import load_dotenv
load_dotenv()

import os
os.environ["TESTING"] = "1"

import pytest
from app import create_app
from app.extensions import db as _db


@pytest.fixture()
def app():
    application = create_app()
    application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    application.config["TESTING"] = True

    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def db(app):
    return _db