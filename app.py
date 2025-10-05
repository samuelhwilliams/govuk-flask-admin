"""
An example app to be used with the govuk-flask-admin theme for testing.
"""

import datetime
import enum
import random
import uuid
from typing import Optional

import faker
from flask import Flask
from flask_admin import Admin
from flask_sqlalchemy_lite import SQLAlchemy
from govuk_flask_admin import GovukFrontendV5_6Theme, GovukFlaskAdmin, GovukModelView
from govuk_frontend_wtf.main import WTFormsHelpers
from jinja2 import PackageLoader, ChoiceLoader, PrefixLoader
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship
from sqlalchemy.testing.schema import mapped_column
from wtforms.validators import Email


class FavouriteColour(enum.Enum):
    RED = "red"
    BLUE = "blue"
    YELLOW = "yellow"


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    age: Mapped[int]
    job: Mapped[str]
    favourite_colour: Mapped[FavouriteColour]
    account: Mapped[Optional["Account"]] = relationship(back_populates="user")
    created_at: Mapped[datetime.date]


class Account(Base):
    __tablename__ = "account"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    user: Mapped[User] = relationship(back_populates="account")


class UserModelView(GovukModelView):
    page_size = 15
    can_set_page_size = True
    page_size_options = [10, 15, 25, 50]

    form_args = {"email": {"validators": [Email()]}}

    # Enable filtering on multiple columns
    column_filters = ["age", "job", "email", "created_at", "favourite_colour"]

    # Enable search
    column_searchable_list = ["email", "name"]

    # Enable export
    can_export = True
    export_types = ["csv"]

    # Add column descriptions for accessibility
    column_descriptions = {
        "age": "User's age in years",
        "email": "Email address for contacting the user",
        "created_at": "Date the user account was created"
    }


def _create_app(config_overrides=None):
    """Application factory for creating Flask app instances.

    Args:
        config_overrides: Dict of config values to override defaults

    Returns:
        Tuple of (app, db, admin) instances
    """
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "oh-no-its-a-secret"
    app.config["EXPLAIN_TEMPLATE_LOADING"] = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SQLALCHEMY_ENGINES"] = {"default": "sqlite:///default.sqlite"}

    # Apply config overrides
    if config_overrides:
        app.config.update(config_overrides)

    # Configure Jinja2 loaders
    app.jinja_options = {
        "loader": ChoiceLoader([
            PrefixLoader({"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}),
            PrefixLoader({"govuk_frontend_wtf": PackageLoader("govuk_frontend_wtf")}),
            PackageLoader("govuk_flask_admin"),
        ])
    }

    # Initialize extensions
    admin = Admin(app, theme=GovukFrontendV5_6Theme())
    govuk_flask_admin = GovukFlaskAdmin(app, service_name="GDS Flask Admin")
    WTFormsHelpers(app)
    db = SQLAlchemy(app)

    # Create tables and add views
    with app.app_context():
        Base.metadata.create_all(db.engine)
        admin.add_view(UserModelView(User, db.session, category="Models"))
        admin.add_view(GovukModelView(Account, db.session, category="Models"))

    seed_database(app, db)

    return app, admin, db


def create_app(config_overrides=None):
    return _create_app(config_overrides)[0]


def seed_database(app, db, num_users=8):
    """Populate database with sample data.

    Args:
        app: Flask application instance
        db: SQLAlchemy database instance
        num_users: Number of sample users to create
    """
    with app.app_context():
        for _ in range(num_users):
            u = User(
                email=faker.Faker().email(),
                created_at=datetime.date.today(),
                name=faker.Faker().name(),
                age=random.randint(18, 100),
                job="blah blah",
                favourite_colour=random.choice(list(FavouriteColour)),
            )
            db.session.add(u)
            db.session.flush()
            a = Account(id=str(uuid.uuid4()), user_id=u.id)
            db.session.add(a)

        db.session.commit()
