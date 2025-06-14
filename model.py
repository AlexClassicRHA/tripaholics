"""Models for travel web app."""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from passlib.hash import argon2
from argon2 import PasswordHasher
from sqlalchemy import create_engine, text


DB_URI = "postgresql://trips_eskt_user:jJlz1FAuXJST60Z0tOypyL8MvFj2mElY@dpg-d0t7u9adbo4c739d7210-a.frankfurt-postgres.render.com/trips_eskt"

ph = PasswordHasher()
db = SQLAlchemy()


class User(db.Model):
    """A user."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    fname = db.Column(db.String, nullable=False)
    lname = db.Column(db.String) # previously nullable=False
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

    trips = db.relationship("Trip", back_populates="user")

    def __repr__(self):
        return f"<User user_id={self.user_id} fname={self.fname} email={self.email}>"


class Trip(db.Model):
    """A trip."""

    __tablename__ = "trips"

    trip_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    traveler = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False) 
    destination = db.Column(db.String, nullable=False)
    trip_title = db.Column(db.String) # default=destination
    longitude = db.Column(db.Float) # test
    latitude = db.Column(db.Float) # test
    start_date = db.Column(db.Date, nullable=False) 
    end_date = db.Column(db.Date, nullable=False) 
    description = db.Column(db.String)
    img = db.Column(db.String)
 
    user = db.relationship("User", back_populates="trips")
    activities = db.relationship("Activity", back_populates="trip")
    reservations = db.relationship("Reservation", back_populates="trip")
    tasks = db.relationship("Checklist", back_populates="trip")

    def __repr__(self):
        return f"<Trip trip_id={self.trip_id} destination={self.destination}>"


class Activity(db.Model):
    """Activity chosen by the user."""

    __tablename__ = "activities"

    activity_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.trip_id"), nullable=False) 
    activity_type = db.Column(db.String) 
    place_name = db.Column(db.String)
    datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    address = db.Column(db.String)
    phone_number = db.Column(db.String(20))
    comments = db.Column(db.String)
    place_img = db.Column(db.String)

    # added relationship
    trip = db.relationship("Trip", back_populates="activities")

    def __repr__(self):
        return f"<Activity activity_id={self.activity_id} activity_type={self.activity_type} activity_name={self.activity_name}>"


class Reservation(db.Model):
    """User's reservation."""

    __tablename__ = "reservations"
    
    reservation_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.trip_id"), nullable=False)
    reservation_type = db.Column(db.String, nullable=False)
    confirmation_info = db.Column(db.String, nullable=False) 
    location = db.Column(db.String, nullable=False)
    start_date = db.Column(db.Date) 
    end_date = db.Column(db.Date)
    notes = db.Column(db.String)

    trip = db.relationship("Trip", back_populates="reservations")

    def __repr__(self):
        return f"<Reservation reservation_id={self.reservation_id} reservation_type={self.reservation_type} location={self.location}>"


class Checklist(db.Model):
    """A checklist."""

    __tablename__ = "tasks"
    
    checklist_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.trip_id"), nullable=False)
    task_title = db.Column(db.String, nullable=False) # or description
    completed = db.Column(db.Boolean, default=False) 

    trip = db.relationship("Trip", back_populates="tasks")

    def __repr__(self):
        return f"<Checklist checklist_id={self.checklist_id} trip_id={self.trip_id} task_title={self.task_title}>"


class Image(db.Model):
    """City's images."""

    __tablename__ = "images"

    img_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    place_name = db.Column(db.String)
    city_name = db.Column(db.String)
    description = db.Column(db.String)
    url = db.Column(db.String)

    def __repr__(self):
        return f"<Image img_id={self.img_id} city_name{self.city_name} place_name={self.place_name}>"



def connect_to_db(flask_app, db_uri=DB_URI, echo=True):
    """Connect to dabatase."""
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    flask_app.config["SQLALCHEMY_ECHO"] = False
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.app = flask_app
    db.init_app(flask_app)

    print("Connected to the db!")


def fake_data():
    """Create some sample data."""

    User.query.delete()
    model.db.session.commit()
    
    ########### Users ###########
    amanda = User(fname="Amanda", lname="Katz", email="amanda@gmail.com", password=ph.hash("1234")) 
    raquel = User(fname="Raquel", lname="Pfeifle", email="raquel@gmail.com", password=ph.hash("1234"))

    db.session.add_all([amanda, raquel])

    ########### Trips ###########
    san_francisco = Trip(
        traveler=amanda.user_id, 
        destination="San Francisco, California", 
        trip_title="My Honeymoon", 
        start_date=datetime.strptime("2022-11-10", "%Y-%m-%d"), 
        end_date=datetime.strptime("2022-11-16", "%Y-%m-%d"), 
        img="Bridge")

    db.session.add(san_francisco)
    amanda.trips.append(san_francisco)

    db.session.commit()


if __name__ == "__main__":
    from server import app

    # Call connect_to_db(app, echo=False) if your program output gets
    # too annoying; this will tell SQLAlchemy not to print out every
    # query it executes.
    
    connect_to_db(app)
    db.create_all()
    fake_data()
