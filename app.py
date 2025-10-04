"""
An example app to be used with the govuk-flask-admin theme for testing.
"""

import datetime
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


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    age: Mapped[int]
    job: Mapped[str]
    account: Mapped[Optional["Account"]] = relationship(back_populates="user")
    created_at: Mapped[datetime.date]


class Account(Base):
    __tablename__ = "account"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    user: Mapped[User] = relationship(back_populates="account")


app = Flask(__name__)
app.config["SECRET_KEY"] = "oh-no-its-a-secret"
app.config["EXPLAIN_TEMPLATE_LOADING"] = True
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.jinja_options = {
    "loader": ChoiceLoader(
        [
            PrefixLoader(
                {"govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja")}
            ),
            PrefixLoader({"govuk_frontend_wtf": PackageLoader("govuk_frontend_wtf")}),
            PackageLoader("govuk_flask_admin"),
        ]
    )
}

app.config["SQLALCHEMY_ENGINES"] = {"default": "sqlite:///default.sqlite"}

admin = Admin(app, theme=GovukFrontendV5_6Theme())
govuk_flask_admin = GovukFlaskAdmin(app, service_name="GDS Flask Admin")
WTFormsHelpers(app)


class UserModelView(GovukModelView):
    page_size = 15

    form_args = {"email": {"validators": [Email()]}}

    column_filters = ["age", "job"]


db = SQLAlchemy(app)
with app.app_context():
    Base.metadata.create_all(db.engine)

    num_to_create = 8
    for _ in range(num_to_create):
        u = User(
            email=faker.Faker().email(),
            created_at=datetime.date.today(),
            name=faker.Faker().name(),
            age=random.randint(18, 100),
            job="blah blah",
        )
        db.session.add(u)
        db.session.flush()
        a = Account(id=str(uuid.uuid4()), user_id=u.id)
        db.session.add(a)

    db.session.commit()

    admin.add_view(UserModelView(User, db.session, category="Models"))
    admin.add_view(GovukModelView(Account, db.session, category="Models"))
