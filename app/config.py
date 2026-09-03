import os
from datetime import timedelta
import logging

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///prospection.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-moi-en-production")

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-moi-aussi-en-production")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    @staticmethod
    def configurer_logs():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
            handlers=[
                logging.FileHandler("app.log", encoding="utf-8"),
                logging.StreamHandler()
            ]
        )