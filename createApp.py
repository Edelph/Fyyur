from models import db
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    db.init_app(app)
    migrate.init_app(app, db)

    return app
