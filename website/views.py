from flask import Blueprint, request, render_template, redirect, url_for
from . import db
from .models import Movie, Director, Loan
from datetime import datetime

views = Blueprint("views", __name__)


@views.route("/movies", methods=["GET", "POST"])
def movies_list():
    if request.method == "POST":
        if "directors" in request.form:
            directors_input = request.form.get("directors")
            directors_list = [
                director.strip() for director in directors_input.split(",")
            ]

            for director_name in directors_list:
                director_name = director_name.title()
                existing_director = Director.query.filter_by(name=director_name).first()
                if not existing_director:
                    new_dir = Director(name=director_name)
                    db.session.add(new_dir)

            db.session.commit()

        title = request.form.get("title")
        opinion = request.form.get("opinion")
        watched = request.form.get("watched")

        watched = bool(watched)

        title = title.title()
        if len(title) < 1:
            return "Za krótki tytuł"
        else:
            new_movie = Movie(
                title=title,
                opinion=opinion,
                watched=watched,
            )

            if "directors" in request.form:
                directors_input = request.form.get("directors")
                directors_list = [
                    director.strip() for director in directors_input.split(",")
                ]

                for director_name in directors_list:
                    director_name = director_name.title()
                    existing_director = Director.query.filter_by(
                        name=director_name
                    ).first()
                    if existing_director:
                        new_movie.directors.append(existing_director)

            db.session.add(new_movie)
            db.session.commit()

    movies = Movie.query.all()
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
        if not existing_director:
            new_dir = Director(
                name=name,
                age=age,
                opinion=opinion,
                best_movie=best_movie,
                worst_movie=worst_movie,
            )
            db.session.add(new_dir)
        db.session.commit()

    return render_template("directors.html", directors=directors)


@views.route("/directors/<int:director_id>", methods=["GET", "POST"])
def get_director(director_id):
    director = Director.query.get(director_id)
    if director is None:
        return "Nie znaleziono reżysera o podanym identyfikatorze."

    if request.method == "POST":
        new_name = request.form.get("name").title()
        age = request.form.get("age")
        opinion = request.form.get("opinion")
        best_movie = request.form.get("best_movie").title()
        worst_movie = request.form.get("worst_movie").title()

        existing_director = Director.query.filter_by(name=new_name).first()

        if not existing_director or existing_director == director:
            director.name = new_name
            director.age = age
            director.opinion = opinion
            director.best_movie = best_movie
            director.worst_movie = worst_movie

            movies_with_old_name = Movie.query.filter(
                Movie.directors.any(id=director_id)
            ).all()
            for movie in movies_with_old_name:
                movie.directors.remove(director)
                movie.directors.append(Director.query.get(director_id))

            db.session.commit()
            return redirect("/directors")

        else:
            return "Reżyser o podanej nazwie już istnieje. Proszę podać inną nazwę."

    return render_template("director.html", director=director)


@views.route("/movies/<int:id>", methods=["GET", "POST"])
def get_movie(id):
    movie = Movie.query.get(id)
    if request.method == "POST":
        title = request.form.get("title").title()
        opinion = request.form.get("opinion")
        watched = request.form.get("watched")

        watched = bool(watched)

        movie.title = title
        movie.opinion = opinion
        movie.watched = watched

        existing_directors = Director.query.filter(
            Director.name.in_(movie.get_director_names())
        ).all()

        for director in existing_directors:
            movie.directors.remove(director)

        for i in range(1, 6):
            director_name = request.form.get(f"director{i}")
            if director_name:
                director_name = director_name.title()
                existing_director = Director.query.filter_by(name=director_name).first()
                if not existing_director:
                    new_dir = Director(name=director_name)
                    db.session.add(new_dir)
                    movie.directors.append(new_dir)
                else:
                    movie.directors.append(existing_director)

        db.session.commit()
        return redirect("/movies")

    return render_template("movie.html", movie=movie)


@views.route("/loans", methods=["GET", "POST"])
def loans_list():
    loans = Loan.query.order_by(Loan.borrowed_date.desc()).all()

    subquery = (
        db.session.query(Loan.movie_id).filter(Loan.returned_date == None).subquery()
    )
    movies = Movie.query.filter(~Movie.id.in_(subquery)).all()

    if request.method == "POST":
        movie_id = request.form.get("movie_id")

        existing_loan = Loan.query.filter_by(
            movie_id=movie_id, returned_date=None
        ).first()
        if existing_loan:
            existing_loan.returned_date = datetime.now()
        else:
            new_loan = Loan(movie_id=movie_id)
            db.session.add(new_loan)
        db.session.commit()

        return redirect("/loans")
    return render_template("loans.html", loans=loans, movies=movies)


@views.route("/return_movie/<int:loan_id>", methods=["POST"])
def return_movie(loan_id):
    loan = Loan.query.get(loan_id)
    if loan:
        loan.returned_date = datetime.utcnow()
        db.session.commit()
    return redirect("/loans")
