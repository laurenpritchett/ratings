"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, jsonify, render_template, redirect, request, flash,
                   session)

from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db, progress_tracker

from sqlalchemy.orm.exc import NoResultFound


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route('/user-login')
def user_login():
    """ """

    return render_template("user-login.html")


@app.route('/user-login', methods=["POST"])
def handle_user_login():
    """Handles login and registration for new users."""

    email = request.form.get("email")
    password = request.form.get("password")

    # Check if user is in the database. If not, create a new user.
    try:
        current_user = User.query.filter(User.email == email).one()
    except NoResultFound:
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Welcome stranger!')
        return redirect("/")

    # Verify that user has entered the correct password.
    if current_user.password == password:
        session['user_id'] = current_user.user_id
        flash('Welcome back!')
        return redirect("/")
    else:
        flash('Incorrect email or password provided.')

    return redirect("/")


@app.route('/user-logout')
def logout():
    """Remove user_id from session and redirect to the home page."""

    del session['user_id']
    flash('Goodbye mate!')
    return redirect("/")


@app.route('/user/<user_id>')
def user_page(user_id):
    """ Show user profile."""

    current_user = User.query.filter(User.user_id == user_id).one()

    title_and_score = db.session.query(Movie.title,
                                       Rating.score).\
        join(Rating).\
        filter(Rating.user_id == user_id).\
        all()

    progress = progress_tracker(user_id)

    return render_template("user-profile.html",
                           current_user=current_user,
                           title_and_score=title_and_score,
                           progress=progress,
                           )


@app.route('/movies')
def show_movies():
    """Show movies in database."""

    movies = Movie.query.all()
    titles = sorted([(movie.title, movie.movie_id) for movie in movies])

    return render_template("movies.html", titles=titles)


@app.route('/movies/<movie_id>')
def show_movie_details(movie_id):
    """Show movie details."""

    user_id = session.get('user_id')
    ratings_query = Rating.query.filter(Rating.movie_id == movie_id)
    ratings = ratings_query.all()
    class_name = "hidden"

    if user_id is not None:
        user_rating = ratings_query.filter(Rating.user_id == user_id).all()
        if user_rating == []:
            user_score = ""
        else:
            user_score = user_rating[0].score
            class_name = "visible"
    else:
        user_score = ""

    scores = [rating.score for rating in ratings]
    title = ratings[0].movie.title

    return render_template('movie-details.html',
                           scores=scores,
                           title=title,
                           user_score=user_score,
                           class_name=class_name
                           )


@app.route('/check-status')
def check_status():
    """Check if user is logged in"""

    user_id = request.args.get('user_id')

    if user_id is None:
        user_id = ""

    return user_id


@app.route('/rate-movie', methods=['POST'])
def rate_movie():
    """Provide new rating or change rating."""

    rating = request.form.get('rating')
    title = request.form.get('title')
    user_id = session['user_id']
    movie = Movie.query.filter(Movie.title == title).all()
    movie_id = movie[0].movie_id
    user_rating = Rating.query.filter((Rating.movie_id == movie_id) & (Rating.user_id == user_id)).all()

    print "user_rating", user_rating

    if user_rating == []:
        new_rating = Rating(user_id=user_id,
                            movie_id=movie_id,
                            score=rating)
        db.session.add(new_rating)

    else:
        user_rating[0].score = rating

    db.session.commit()

    return "Your rating was successful!"

@app.route("/search-results")
def search_movie():
    """Return results from movie search."""

    title = request.args.get('movie-search')
    search_title = '%{}%'.format(title)
    movies = Movie.query.filter(Movie.title.ilike(search_title)).all()
    titles = sorted([(movie.title, movie.movie_id) for movie in movies])

    return render_template("search-results.html", titles=titles)

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)



    app.run(port=5000, host='0.0.0.0')
