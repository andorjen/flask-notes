
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

db = SQLAlchemy()


def connect_db(app):
    """Models for flask-notes."""
    db.app = app
    db.init_app(app)


class User(db.Model):
    """User"""
    __tablename__ = "users"

    username = db.Column(
        db.String(20),
        primary_key=True)

    password = db.Column(
        db.String(100),
        nullable=False)

    email = db.Column(
        db.String(50),
        nullable=False)

    first_name = db.Column(
        db.String(30),
        nullable=False)

    last_name = db.Column(
        db.String(30),
        nullable=False)

    notes = db.relationship(
        'Note',
        backref='author')

    @classmethod  # anything related to adding to database should be in class methods; not commit
    # instanciate user here and all add to db, but not commit; the additional
    # pass in additional parameters, remove line 43
    def register(cls, username, password, email, first_name, last_name):
        """register user with hashed pasword and return user"""

        hashed = bcrypt.generate_password_hash(password).decode('utf8')

        user = User(username=username,
                    password=hashed,
                    email=email,
                    first_name=first_name,
                    last_name=last_name)

        db.session.add(user)

        return user

    @classmethod
    def authenticate(cls, username, password):
        """validate that user exists and password is correct.
        return user if valid, else return false
        """

        u = cls.query.filter_by(username=username).one_or_none()
        if u and bcrypt.check_password_hash(u.password, password):
            return u
        else:
            return False


class Note(db.Model):
    """Note"""

    __tablename__ = "notes"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True)

    title = db.Column(
        db.String(100),
        nullable=False)

    content = db.Column(
        db.Text,
        nullable=False)

    owner = db.Column(
        db.String,
        db.ForeignKey("users.username"),
        nullable=False)
