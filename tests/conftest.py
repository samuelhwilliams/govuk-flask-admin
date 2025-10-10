"""Shared pytest fixtures for all tests."""
import pytest
import datetime
import random

# Import from app.py instead of redefining
from app import create_app, User, Account, Post, Base, FavouriteColour, _create_app

# Store app components at module level for session scope
_app_components = None


def get_app_components():
    """Get or create app components (app, db, admin) for testing."""
    global _app_components
    if _app_components is None:
        _app_components = _create_app(config_overrides={
            "TESTING": True,
            "SQLALCHEMY_ENGINES": {"default": "sqlite:///:memory:"},
        })
    return _app_components


@pytest.fixture(scope="session")
def app():
    """Create test Flask app using factory."""
    app, db, admin = get_app_components()
    return app


@pytest.fixture(scope="session")
def db(app):
    """Get database instance from factory."""
    app, db, admin = get_app_components()
    return db


@pytest.fixture(scope="session")
def admin_instance(app):
    """Get Flask-Admin instance from factory."""
    app, db, admin = get_app_components()
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

        # Create posts for each user
        for i, user in enumerate(users):
            # Create 2-3 posts per user
            for j in range(2 + (i % 2)):
                published = None
                if j > 0:  # First post is draft, others are published
                    published = datetime.datetime(2024, 1, 1, 12, 0, 0) + datetime.timedelta(days=i * 3 + j)

                post = Post(
                    title=f"Post {j + 1} by User {i}",
                    content=f"This is the content of post {j + 1} written by {user.name}.",
                    author_id=user.id,
                    published_at=published,
                    created_at=datetime.datetime(2024, 1, 1, 10, 0, 0) + datetime.timedelta(days=i * 3 + j)
                )
                db.session.add(post)

        db.session.commit()
        yield users

        # Cleanup
        db.session.query(Post).delete()
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
