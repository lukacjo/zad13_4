from . import db
from datetime import datetime
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

# Tabela łącząca dla relacji wiele do wielu
movie_director_association = Table(
    "movie_director_association",
    db.Model.metadata,
    Column("movie_id", Integer, ForeignKey("movie.id")),
    Column("director_id", Integer, ForeignKey("director.id")),
)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    opinion = db.Column(db.String(500))
    watched = db.Column(db.Boolean, default=True)
    directors = db.relationship(
        "Director", secondary=movie_director_association, back_populates="movies"
    )

    loan = db.relationship("Loan", back_populates="movie", uselist=False)

    def is_rented(self):
        # Sprawdzam czy film jest wypoyczony czy nie
        active_loan = Loan.query.filter_by(movie_id=self.id, returned_date=None).first()
        return active_loan is not None

    def get_director_names(self):
        return [director.name for director in self.directors]


class Director(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    age = db.Column(db.Integer)
    opinion = db.Column(db.String(500))
    best_movie = db.Column(db.String(100))
    worst_movie = db.Column(db.String(100))
    movies = db.relationship(
        "Movie", secondary=movie_director_association, back_populates="directors"
    )


class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"), nullable=False)
    borrowed_date = db.Column(db.DateTime, default=datetime.now)
    returned_date = db.Column(db.DateTime, nullable=True)

    movie = db.relationship("Movie", back_populates="loan")
