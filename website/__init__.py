from flask import Flask
from os import path
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "nininini"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"

    db.init_app(app)

    from .views import views

    app.register_blueprint(views, url_prefix="/")

    from .models import Movie, Director  # importuje modele do tworzenia danych w bazie

    with app.app_context():  # tworze te bazy danych
        db.create_all()

    return app
