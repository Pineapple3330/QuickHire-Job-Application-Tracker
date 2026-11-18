
import os

class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "quickhire-development-secret"
    )

    SQLALCHEMY_DATABASE_URI = "sqlite:///quickhire.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
