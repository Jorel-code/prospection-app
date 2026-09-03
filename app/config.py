import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)

DEFAULT_DB_PATH = os.path.join(INSTANCE_DIR, "prospection.db").replace("\\", "/")


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-moi-en-production")

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-moi-aussi-en-production")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    API_TITLE = "Prospection App API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/docs"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    @staticmethod
    def configurer_logs():
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
            handlers=[
                logging.FileHandler("app.log", encoding="utf-8"),
                logging.StreamHandler()
            ]
        )