from . import db
import uuid


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    opinion = db.Column(db.String(500))
    watched = db.Column(db.Boolean, default=True)
    rented = db.Column(db.Boolean, default=False)
    director_name = db.Column(db.String, db.ForeignKey("director.name"))


class Director(db.Model):
    name = db.Column(db.String(100), primary_key=True)
    age = db.Column(db.Integer)
    opinion = db.Column(db.String(500))
    best_movie = db.Column(db.String(100))
    worst_movie = db.Column(db.String(100))
    movies = db.relationship("Movie")
