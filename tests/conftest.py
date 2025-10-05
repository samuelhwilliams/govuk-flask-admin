"""Shared pytest fixtures for all tests."""
import pytest
import datetime
import random
import uuid
from flask import Flask
from flask_admin import Admin
from flask_sqlalchemy_lite import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship, mapped_column
from govuk_flask_admin import GovukFrontendV5_6Theme, GovukFlaskAdmin, GovukModelView
from govuk_frontend_wtf.main import WTFormsHelpers
from jinja2 import PackageLoader, ChoiceLoader, PrefixLoader
import enum


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
    account: Mapped["Account"] = relationship(back_populates="user", uselist=False)
    created_at: Mapped[datetime.date]


class Account(Base):
    __tablename__ = "account"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    user: Mapped[User] = relationship(back_populates="account")


@pytest.fixture(scope="session")
def app():
    """Create test Flask app."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test-secret-key"
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_ENGINES"] = {"default": "sqlite:///:memory:"}

    # Configure Jinja2 loaders
    app.jinja_options = {
        "loader": ChoiceLoader([
            PrefixLoader({"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}),
            PrefixLoader({"govuk_frontend_wtf": PackageLoader("govuk_frontend_wtf")}),
            PackageLoader("govuk_flask_admin"),
        ])
    }

    return app


@pytest.fixture(scope="session")
def db(app):
    """Create test database."""
    db = SQLAlchemy(app)

    with app.app_context():
        Base.metadata.create_all(db.engine)

    return db


@pytest.fixture(scope="session")
def admin_instance(app, db):
    """Create Flask-Admin instance with GOV.UK theme and views."""
    admin = Admin(app, theme=GovukFrontendV5_6Theme())
    govuk_flask_admin = GovukFlaskAdmin(app, service_name="Test Admin")
    WTFormsHelpers(app)

    # Add views immediately to avoid registration after first request
    class TestUserModelView(GovukModelView):
        page_size = 15
        can_set_page_size = True
        page_size_options = [10, 15, 25, 50]
        column_filters = ["age", "job", "email", "created_at", "favourite_colour"]
        column_searchable_list = ["email", "name"]
        can_export = True
        export_types = ["csv"]
        column_descriptions = {
            "age": "User's age in years",
            "email": "Email address for contacting the user",
        }

    with app.app_context():
        user_view = TestUserModelView(User, db.session, category="Models", name="User")
        admin.add_view(user_view)

        account_view = GovukModelView(Account, db.session, category="Models", name="Account")
        admin.add_view(account_view)

    return admin


@pytest.fixture(scope="session")
def user_model_view(admin_instance):
    """Get UserModelView from admin instance."""
    # Find the user view from registered views
    for view in admin_instance._views:
        if view.name == "User":
            return view
    raise RuntimeError("UserModelView not found")


@pytest.fixture
def sample_users(db, app):
    """Create sample users for testing."""
    with app.app_context():
        users = []
        for i in range(10):
            user = User(
                email=f"user{i}@example.com",
                name=f"Test User {i}",
                age=20 + i,
                job=f"Job {i % 3}",
                favourite_colour=list(FavouriteColour)[i % 3],
                created_at=datetime.date(2024, 1, 1) + datetime.timedelta(days=i)
            )
            db.session.add(user)
            users.append(user)

        db.session.commit()
        yield users

        # Cleanup
        db.session.query(Account).delete()
        db.session.query(User).delete()
        db.session.commit()


@pytest.fixture(scope="session")
def account_model_view(admin_instance):
    """Get AccountModelView from admin instance."""
    # Find the account view from registered views
    for view in admin_instance._views:
        if view.name == "Account":
            return view
    raise RuntimeError("AccountModelView not found")


@pytest.fixture
def client(app, admin_instance):
    """Create test client with views registered."""
    return app.test_client()
