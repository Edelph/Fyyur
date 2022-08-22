
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False, unique=True)
    image_link = db.Column(db.String(500), nullable=False, unique=True)
    facebook_link = db.Column(db.String(120), unique=True)
    website_link = db.Column(db.String(500), unique=True)
    seeking_talent = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(), nullable=False)
    genres = db.Column(db.JSON, nullable=False)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False, unique=True)
    image_link = db.Column(db.String(500), nullable=False, unique=True)
    facebook_link = db.Column(db.String(120), unique=True)
    website_link = db.Column(db.String(500), unique=True)
    seeking_description = db.Column(db.String(), nullable=False)
    seeking_venue = db.Column(db.Boolean, nullable=True, default=False)
    genres = db.Column(db.JSON, nullable=False)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'))
    artist_id = db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'))
    start_time = db.Column(db.DateTime, nullable=True)

    artist = db.relationship(Artist, backref="shows")
    venue = db.relationship(Venue, backref="shows")


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
