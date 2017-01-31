"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from sqlalchemy import func
from model import User, Rating, Movie, connect_to_db, db
from server import app

from datetime import datetime


def load_users():
    """Load users from u.user into database."""

    print "Users"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    for row in open("seed_data/u.user"):
        row = row.rstrip()
        user_id, age, gender, occupation, zipcode = row.split("|")

        user = User(user_id=user_id,
                    age=age,
                    zipcode=zipcode)

        # We need to add to the session or it won't ever be stored
        db.session.add(user)

    # Once we're done, we should commit our work
    db.session.commit()


def load_movies():
    """Load movies from u.item into database."""

    print "Movies"

    Movie.query.delete()

    for i, row in enumerate(open("seed_data/u.item")):
        row = row.rstrip()

        movie_id, title, released_str, _, imdb_url = row.split("|")[:5]

        # Convert date string to datetime object.
        # The date in the file is Day-Month-Year.

        if released_str:
            released_at = datetime.strptime(released_str, "%d-%b-%Y")
        else:
            released_at = None

        # Remove the year (ie "(2005)") from the end of the title.

        title = title.split("(")[0]

        movie = Movie(movie_id=movie_id,
                      title=title,
                      released_at=released_at,
                      imdb_url=imdb_url)

        db.session.add(movie)

        # Inform the user of progress.
        if i % 100 == 0:
            print i

    db.session.commit()


def load_ratings():
    """Load ratings from u.data into database.

       Data looks like:
       user_id \t movie_id \t score \t timestamp.
    """

    print "Ratings"

    Rating.query.delete()

    for i, row in enumerate(open("seed_data/u.data")):
        row = row.rstrip()
        user_id, movie_id, score = row.split("\t")[:3]

        rating = Rating(user_id=user_id,
                        movie_id=movie_id,
                        score=score,
                        )

        db.session.add(rating)

        if i % 1000 == 0:
            print i

            # Commit every 1000 rows to increase performance
            # and prevent thrashing.

            db.session.commit()

    db.session.commit()


def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_movies()
    load_ratings()
    set_val_user_id()
