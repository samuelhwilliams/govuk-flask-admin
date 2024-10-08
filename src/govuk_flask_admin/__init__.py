import glob
import inspect
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Literal

from flask import Flask, Blueprint, url_for, send_from_directory
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.form import AdminModelConverter
from flask_admin.contrib.sqla.tools import is_relationship
from flask_admin.theme import Theme
from govuk_frontend_wtf.wtforms_widgets import GovTextInput
from sqlalchemy.orm import ColumnProperty

ROOT_DIR = Path(__file__).parent


@dataclass
class GovukFrontendV5_6Theme(Theme):
    folder: str = 'admin'
    base_template: str = 'admin/base.html'


def govuk_pagination_params_builder(page_zero_indexed, total_pages, url_generator):
    """Builds the `params` argument for govukPagination based on govuk-frontend-jinja.

    This is fed by values from Flask-Admin's pagination, which provides:
        arg 1 (`page`) as a 0-indexed reference to the current page; but
        arg 2 (`pages`) as the number of total pages rather than the max page as a 0-indexed thing
    """
    component_params = {}

    if page_zero_indexed != 0:
        component_params['previous'] = {"href": url_generator(page_zero_indexed - 1)}

    if page_zero_indexed + 1 != total_pages:
        component_params['next'] = {"href": url_generator(page_zero_indexed + 1)}

    if total_pages <= 3:
        items = [
            {"number": x + 1, "current": page_zero_indexed == x, "href": url_generator(x)}
            for x in range(1, total_pages + 1)
        ]

    else:
        items = []
        num_pages_around_current = 2

        pages_to_show = {0, page_zero_indexed, total_pages - 1}
        for x in range(1, num_pages_around_current + 1):
            pages_to_show.add(max(0, page_zero_indexed - x))
            pages_to_show.add(min(total_pages - 1, page_zero_indexed + x))

        last = -1
        for curr in sorted(pages_to_show):
            if last + 1 < curr:
                items.append({"ellipsis": True})

            items.append({"number": curr + 1, "current": page_zero_indexed == curr, "href": url_generator(curr)})
            last = curr

    component_params['items'] = items

    return component_params



def govuk_flask_admin_assets_tags():
    manifest_path = ROOT_DIR / "static" / "govuk-frontend"

    js_file = Path(glob.glob(f"{manifest_path}/*.js")[0]).name
    css_file = Path(glob.glob(f"{manifest_path}/*.css")[0]).name

    js_file_url = url_for("govuk_flask_admin.static", filename=js_file)
    css_file_url = url_for("govuk_flask_admin.static", filename=css_file)

    return dedent(
        f"""
            <!-- FLASK_VITE_HEADER -->
            <script type="module" src="{js_file_url}"></script>
            <link rel="stylesheet" href="{css_file_url}"></link>
        """
    ).strip()


class GovukFlaskAdmin:
    def __init__(self, app: Flask):
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        self._blueprint = Blueprint('govuk_flask_admin', 'govuk_flask_admin', static_folder='static', template_folder='templates')

        app.route(
            "/_govuk_flask_admin/<path:filename>", endpoint="govuk_flask_admin.static"
        )(self.static)
        app.template_global('govuk_flask_admin_assets_tags')(govuk_flask_admin_assets_tags)
        app.template_global('govuk_pagination_data_builder')(govuk_pagination_params_builder)

    def static(
        self, filename, vite_routes_host: str | None = None  # noqa: ARG002
    ):
        dist = str(ROOT_DIR / "static" / "govuk-frontend")
        return send_from_directory(dist, filename, max_age=60 * 60 * 24 * 7 * 52)


def widget_for_sqlalchemy_type(*args):
    def _inner(func):
        func._widget_converter_for = frozenset(args)
        return func
    return _inner


class GovukAdminModelConverter(AdminModelConverter):
    def __init__(self, session, view):
        super().__init__(session, view)

        self.sqlalchemy_type_widgets = {
            "String": GovTextInput(),
            "Integer": GovTextInput(),
        }

        self.sqlalchemy_type_widget_args = {
            "String": {},
            "Integer": {"params": {"inputmode": "numeric"}},
        }

    def map_column_via_lookup_table(self, column, lookup: Literal['sqlalchemy_type_widgets', 'sqlalchemy_type_widget_args']):
        lookup_table = getattr(self, lookup)

        if self.use_mro:
            types = inspect.getmro(type(column.type))
        else:
            types = [type(column.type)]

        # Search by module + name
        for col_type in types:
            type_string = '%s.%s' % (col_type.__module__, col_type.__name__)

            if type_string in lookup_table:
                return lookup_table[type_string]

        # Search by name
        for col_type in types:
            if col_type.__name__ in lookup_table:
                return lookup_table[col_type.__name__]

        return None


class GovukModelView(ModelView):
    model_form_converter = GovukAdminModelConverter

    def _resolve_widget_class_for_sqlalchemy_column(self, prop: ColumnProperty):
        return GovTextInput

    def _iterate_model_fields(self):
        mapper = self.model._sa_class_manager.mapper

        for attr in mapper.attrs:
            if is_relationship(attr):
                continue

            column_name = attr.key
            column = getattr(self.model, column_name)
            yield column_name, column


    def _populate_implicit_form_args(self):
        if not self.form_args:
            self.form_args = {}

        converter = self.model_form_converter(self.session, self)

        form_args = {}
        for column_name, column in self._iterate_model_fields():
            govuk_widget = converter.map_column_via_lookup_table(column, 'sqlalchemy_type_widgets')

            form_args[column_name] = {
                "widget": govuk_widget
            }

        self.form_args = {**form_args, **self.form_args}

    def _populate_implicit_form_widget_args(self):
        if not self.form_widget_args:
            self.form_widget_args = {}

        converter = self.model_form_converter(self.session, self)

        form_widget_args = {}
        for column_name, column in self._iterate_model_fields():
            form_widget_args[column_name] = converter.map_column_via_lookup_table(column, 'sqlalchemy_type_widget_args')

        self.form_widget_args = {**form_widget_args, **self.form_widget_args}

    def scaffold_form(self):
        """
            Create form from the model.
        """
        self._populate_implicit_form_args()
        self._populate_implicit_form_widget_args()

        return super().scaffold_form()
