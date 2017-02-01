"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, jsonify, render_template, redirect, request, flash,
                   session)

from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db

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
    """ """

    email = request.form.get("email")
    password = request.form.get("password")

    try:
        current_user = User.query.filter(User.email == email).one()
    except NoResultFound:
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Welcome stranger!')
        return redirect("/")

    if current_user.password == password:
        session['user_id'] = current_user.user_id
        flash('Welcome back!')
        return redirect("/")
    else:
        flash('Incorrect email or password provided.')

    # test the email against the db
    # except:

    return redirect("/")


@app.route('/user-logout')
def logout():
    """ """

    session.pop['user_id']
    flash('Goodbye mate!')
    return redirect("/")


@app.route('/user/<user_id>')
def user_page(user_id):
    """ Show user profile."""

    current_user = User.query.filter(User.user_id == user_id).one()

    title_and_score = db.session.query(Movie.title,
                                       Rating.score).join(Rating).filter(Rating.user_id == user_id).all()

    return render_template("user-profile.html",
                           current_user=current_user,
                           title_and_score=title_and_score,
                           )


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)



    app.run(port=5000, host='0.0.0.0')
