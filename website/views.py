from collections import namedtuple
from flask import Blueprint, request, render_template, redirect, url_for
from . import db
from .models import Movie, Director

views = Blueprint("views", __name__)


@views.route("/movies", methods=["GET", "POST"])
def movies_list():
    if request.method == "POST":
        title = request.form.get("title")
        opinion = request.form.get("opinion")
        director_name = request.form.get("director")
        watched = request.form.get("watched")
        rented = request.form.get("rented")

        if rented is None:
            rented = False
        else:
            rented = True

        if watched is None:
            watched = False
        else:
            watched = True

        director_name = director_name.title()
        title = title.title()
        if len(title) < 1:
            return "Za krótki tytuł"
        else:
            new_movie = Movie(
                title=title,
                opinion=opinion,
                director_name=director_name,
                watched=watched,
                rented=rented,
            )  # wsadzam dane do wczesniej przygotowanego modelu żeby potem poszło do bazy naych
            existing_director = Director.query.filter_by(name=director_name).first()
            if existing_director:
                pass
            else:
                new_dir = Director(name=director_name)
                db.session.add(new_dir)
            db.session.add(new_movie)  # Dodawanie notatki do bazy danych
            # sprawdzić jeszcze czy dany reyser jest w bazie danych i wtedy nie dodawać albo zrobić e name jest unique
            db.session.commit()

    movies = Movie.query
    return render_template("movies.html", movies=movies)


@views.route("/directors", methods=["GET", "POST"])
def directors_list():
    directors = Director.query
    if request.method == "POST":
        name = request.form.get("name").title()
        age = request.form.get("age")
        opinion = request.form.get("opinion")
        best_movie = request.form.get("best_movie").title()
        worst_movie = request.form.get("worst_movie").title()

        existing_director = Director.query.filter_by(name=name).first()
        if existing_director:
            pass
        else:
            new_dir = Director(
                name=name,
                age=age,
                opinion=opinion,
                best_movie=best_movie,
                worst_movie=worst_movie,
            )  # wsadzam dane do wczesniej przygotowanego modelu eby potem poszło do bazy naych
            db.session.add(new_dir)  # Dodawanie notatki do bazy danych
        db.session.commit()

    return render_template("directors.html", directors=directors)


@views.route("/directors/<string:name_dir>", methods=["GET", "POST"])
def get_director(name_dir):
    director = Director.query.get(name_dir)
    movie = None
    if request.method == "POST":
        name = request.form.get("name").title()
        age = request.form.get("age")
        opinion = request.form.get("opinion")
        best_movie = request.form.get("best_movie").title()
        worst_movie = request.form.get("worst_movie").title()

        director.name = name
        director.age = age
        director.opinion = opinion
        director.best_movie = best_movie
        director.worst_movie = worst_movie

        movies_with_old_name = Movie.query.filter_by(director_name=name_dir).all()
        for movie in movies_with_old_name:
            movie.director_name = name

        db.session.merge(director)
        if movie is not None:
            db.session.merge(movie)

        db.session.commit()
        return redirect("/directors")

    return render_template("director.html", director=director)


@views.route("/movies/<int:id>", methods=["GET", "POST"])
def get_movie(id):
    movie = Movie.query.get(id)
    if request.method == "POST":
        title = request.form.get("title").title()
        opinion = request.form.get("opinion")
        director_name = request.form.get("director")
        watched = request.form.get("watched")
        rented = request.form.get("rented")

        if rented is None:
            rented = False
        else:
            rented = True

        if (
            watched == None
        ):  # musze tak bo teraz jestem zbyt zmęczony zeby ogarnąć to potrawnie
            watched = False
        else:
            watched = True

        movie.title = title
        movie.opinion = opinion
        movie.director_name = director_name
        movie.watched = watched
        movie.rented = rented

        existing_director = Director.query.filter_by(name=director_name).first()
        if not existing_director:
            new_dir = Director(name=director_name)
            db.session.add(new_dir)

        db.session.merge(movie)  # Aktualizacja notatki w bazie danych
        db.session.commit()
        return redirect("/movies")

    return render_template("movie.html", movie=movie)
