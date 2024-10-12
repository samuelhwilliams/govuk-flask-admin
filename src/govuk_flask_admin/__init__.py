import glob
import inspect
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
import typing as t

from flask import Flask, url_for, send_from_directory, request
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.form import AdminModelConverter
from flask_admin.contrib.sqla.tools import is_relationship
from flask_admin.theme import Theme
from govuk_frontend_wtf.wtforms_widgets import GovTextInput, GovDateInput
from sqlalchemy.orm import ColumnProperty

ROOT_DIR = Path(__file__).parent


@dataclass
class GovukFrontendV5_6Theme(Theme):
    folder: str = "admin"
    base_template: str = "admin/base.html"


def govuk_pagination_params_builder(page_zero_indexed, total_pages, url_generator):
    """Builds the `params` argument for govukPagination based on govuk-frontend-jinja.

    This is fed by values from Flask-Admin's pagination, which provides:
        arg 1 (`page`) as a 0-indexed reference to the current page; but
        arg 2 (`pages`) as the number of total pages rather than the max page as a 0-indexed thing
    """
    component_params = {}

    if page_zero_indexed != 0:
        component_params["previous"] = {"href": url_generator(page_zero_indexed - 1)}

    if page_zero_indexed + 1 != total_pages:
        component_params["next"] = {"href": url_generator(page_zero_indexed + 1)}

    if total_pages <= 3:
        items = [
            {
                "number": x + 1,
                "current": page_zero_indexed == x,
                "href": url_generator(x),
            }
            for x in range(0, total_pages)
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

            items.append(
                {
                    "number": curr + 1,
                    "current": page_zero_indexed == curr,
                    "href": url_generator(curr),
                }
            )
            last = curr

    component_params["items"] = items

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
    def __init__(self, app: Flask, service_name: str | None = None):
        self.service_name = service_name

        if app is not None:
            self.init_app(app)

    def __inject_jinja2_global_variables(self, app):
        @app.context_processor
        def inject_govuk_flask_admin_globals():
            return {"govuk_flask_admin_service_name": self.service_name}

        app.template_global("govuk_flask_admin_assets_tags")(
            govuk_flask_admin_assets_tags
        )
        app.template_global("govuk_pagination_data_builder")(
            govuk_pagination_params_builder
        )

    def __setup_static_routes(self, app):
        if not app.url_map.host_matching:
            app.route(
                "/_govuk_flask_admin/<path:filename>",
                endpoint="govuk_flask_admin.static",
            )(self.static)

        else:
            app.route(
                "/_govuk_flask_admin/<path:filename>",
                endpoint="govuk_flask_admin.static",
                host="<govuk_flask_admin_host>",
            )(self.static)

            @app.url_defaults
            def inject_admin_routes_host_if_required(
                endpoint: str, values: t.Dict[str, t.Any]
            ) -> None:
                if app.url_map.is_endpoint_expecting(
                    endpoint, "govuk_flask_admin_host"
                ):
                    values.setdefault("govuk_flask_admin_host", request.host)

            # Automatically strip `admin_routes_host` from the endpoint values so
            # that the view methods don't receive that parameter, as it's not actually
            # required by any of them.
            @app.url_value_preprocessor
            def strip_admin_routes_host_from_static_endpoint(
                endpoint: t.Optional[str], values: t.Optional[t.Dict[str, t.Any]]
            ) -> None:
                if (
                    endpoint
                    and values
                    and app.url_map.is_endpoint_expecting(
                        endpoint, "govuk_flask_admin_host"
                    )
                ):
                    values.pop("govuk_flask_admin_host", None)

    def init_app(self, app: Flask, service_name: str | None = None):
        service_name = service_name or self.service_name

        self.__inject_jinja2_global_variables(app)
        self.__setup_static_routes(app)

    def static(self, filename):
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

        self.sqlalchemy_type_field_args = {
            "String": {"widget": GovTextInput()},
            "Integer": {"widget": GovTextInput()},
            "Date": {"widget": GovDateInput(), "format": "%d %m %Y"},
        }

        self.sqlalchemy_type_widget_args = {
            "String": {},
            "Integer": {"params": {"inputmode": "numeric"}},
        }

    def map_column_via_lookup_table(
        self,
        column,
        lookup: t.Literal["sqlalchemy_type_field_args", "sqlalchemy_type_widget_args"],
    ):
        lookup_table = getattr(self, lookup)

        if self.use_mro:
            types = inspect.getmro(type(column.type))
        else:
            types = [type(column.type)]

        # Search by module + name
        for col_type in types:
            type_string = "%s.%s" % (col_type.__module__, col_type.__name__)

            if type_string in lookup_table:
                return lookup_table[type_string]

        # Search by name
        for col_type in types:
            if col_type.__name__ in lookup_table:
                return lookup_table[col_type.__name__]

        return None


class GovukModelView(ModelView):
    model_form_converter = GovukAdminModelConverter

    def __init__(
        self,
        model,
        session,
        name=None,
        category="Miscellaneous",
        endpoint=None,
        url=None,
        static_folder=None,
        menu_class_name=None,
        menu_icon_type=None,
        menu_icon_value=None,
    ):
        # To simplify the sidebar and ensure the subnav groups well, we force a default category.
        # Suggest overriding this though.
        super().__init__(
            model,
            session,
            name=name,
            category=category,
            endpoint=endpoint,
            url=url,
            static_folder=static_folder,
            menu_class_name=menu_class_name,
            menu_icon_type=menu_icon_type,
            menu_icon_value=menu_icon_value,
        )

    def _resolve_widget_class_for_sqlalchemy_column(self, prop: ColumnProperty):
        return GovTextInput

    def _iterate_model_fields(self):
        mapper = self.model._sa_class_manager.mapper

        for attr in mapper.attrs:
            if is_relationship(attr) or getattr(attr, "_is_relationship"):
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
            form_field_args = (
                converter.map_column_via_lookup_table(
                    column, "sqlalchemy_type_field_args"
                )
                or {}
            )

            form_args[column_name] = form_field_args

        # For each form field, override the default top-level keys with any provided
        # by the subclass.
        for field_name, field_args in form_args.items():
            form_args[field_name] = {**field_args, **self.form_args.get(field_name, {})}

        self.form_args = form_args

    def _populate_implicit_form_widget_args(self):
        if not self.form_widget_args:
            self.form_widget_args = {}

        converter = self.model_form_converter(self.session, self)

        form_widget_args = {}
        for column_name, column in self._iterate_model_fields():
            form_widget_args[column_name] = (
                converter.map_column_via_lookup_table(
                    column, "sqlalchemy_type_widget_args"
                )
                or {}
            )

        self.form_widget_args = {**form_widget_args, **self.form_widget_args}

    def scaffold_form(self):
        """
        Create form from the model.
        """
        self._populate_implicit_form_args()
        self._populate_implicit_form_widget_args()

        return super().scaffold_form()
