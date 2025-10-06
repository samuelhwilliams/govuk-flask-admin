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
from flask_admin.model.form import converts
from govuk_frontend_wtf.wtforms_widgets import GovTextInput, GovDateInput, GovSelect
from sqlalchemy.orm import ColumnProperty
from wtforms import validators, SelectField
from enum import Enum

# Monkey patch for Flask-Admin fields to work with govuk_frontend_wtf widgets
# These fields don't have _value() method which the widgets expect
try:
    from flask_admin.form.fields import Select2Field
    if not hasattr(Select2Field, '_value'):
        def _value(self):
            if self.data is not None:
                return str(self.data)
            return ''
        Select2Field._value = _value
except ImportError:
    pass

try:
    from wtforms_sqlalchemy.fields import QuerySelectField
    if not hasattr(QuerySelectField, '_value'):
        def _value(self):
            if self.data is not None:
                # For relationship fields, get the primary key value
                if hasattr(self.data, 'id'):
                    return str(self.data.id)
                return str(self.data)
            return ''
        QuerySelectField._value = _value
except ImportError:
    pass


ROOT_DIR = Path(__file__).parent.parent


@dataclass
class GovukFrontendTheme(Theme):
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
    component_params['classes'] = 'govuk-!-text-align-center'

    return component_params


def govuk_flask_admin_assets_tags():
    manifest_path = ROOT_DIR / "assets" / "dist" / "assets"
    print(manifest_path)

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
        dist = str(ROOT_DIR / "assets" / "dist" / "assets")
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

    @converts("sqlalchemy.sql.sqltypes.Enum")
    def convert_enum(self, column, field_args, **extra):
        """Convert Enum columns to GOV.UK select fields."""
        # Build choices: value=enum.name (e.g., 'RED'), label=enum.value (e.g., 'red')
        available_choices = [(e.name, e.value) for e in column.type.enum_class]
        accepted_values = [choice[0] for choice in available_choices]

        if column.nullable:
            field_args["allow_blank"] = column.nullable
            accepted_values.append(None)
            # Add blank choice at the beginning
            available_choices.insert(0, ("", ""))

        self._nullable_common(column, field_args)

        field_args["choices"] = available_choices
        field_args["validators"].append(validators.AnyOf(accepted_values))
        field_args["coerce"] = lambda v: v.name if isinstance(v, Enum) else str(v) if v else v
        field_args["widget"] = GovSelect()

        return SelectField(**field_args)

    # TODO: WIP finish fixing up error messages from wtforms
    # def convert(self, model, mapper, name, prop, field_args, hidden_pk):
    #     field = super().convert(model, mapper, name, prop, field_args, hidden_pk)
    #
    #     if field:
    #         for validator in field.kwargs.get("validators"):
    #             if isinstance(validator, InputRequired):
    #                 validator.message = f"Enter a value for {name.replace('_', ' ')}"
    #
    #     return field


class GovukModelView(ModelView):
    model_form_converter = GovukAdminModelConverter

    # Format enum values to show their .value (lowercase) instead of .name (uppercase)
    column_type_formatters = {
        Enum: lambda view, value, name: value.value if isinstance(value, Enum) else value
    }

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

    def _get_list_filter_args(self):
        """
        Override to combine GOV.UK date input fields before processing filters.

        GOV.UK date inputs create three separate fields with -day, -month, -year suffixes.
        Flask-Admin expects a single field with YYYY-MM-DD format. This method intercepts
        the request parameters and combines the GOV.UK date fields before passing them to
        Flask-Admin's filter processing.
        """
        from flask import request
        from werkzeug.datastructures import ImmutableMultiDict

        # Build modified args dict, filtering out empty filter values
        modified = {}
        for key in request.args.keys():
            # Get all values for this key (handles multi-value params)
            values = request.args.getlist(key)

            # Skip empty filter parameters (but keep non-filter params like search, page, etc.)
            # Filter params start with 'flt' followed by digits
            if key.startswith('flt') and all(v == '' or (isinstance(v, str) and v.strip() == '') for v in values):
                continue

            if len(values) == 1:
                modified[key] = values[0]
            else:
                modified[key] = values

        # Find and combine GOV.UK date fields
        # Look for fields ending with -day that start with 'flt'
        for arg in request.args:
            if arg.startswith('flt') and arg.endswith('-day'):
                base = arg[:-4]  # Remove '-day' suffix
                month_key = base + '-month'
                year_key = base + '-year'

                if month_key in request.args and year_key in request.args:
                    day = request.args[arg].strip()
                    month = request.args[month_key].strip()
                    year = request.args[year_key].strip()

                    # Only combine if all three parts are present
                    if day and month and year:
                        # Create YYYY-MM-DD format, padding day and month to 2 digits
                        modified[base] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

                        # Remove the individual component fields so they don't interfere
                        modified.pop(arg, None)
                        modified.pop(month_key, None)
                        modified.pop(year_key, None)

        # Temporarily replace request.args with modified version
        original_args = request.args
        request.args = ImmutableMultiDict(modified)

        try:
            # Call parent implementation with modified request.args
            result = super()._get_list_filter_args()
        finally:
            # Restore original request.args
            request.args = original_args

        return result

    def _get_remove_filter_url(
        self,
        filter_position,
        active_filters,
        return_url,
        sort_column,
        sort_desc,
        search,
        page_size,
        default_page_size,
        extra_args
    ):
        """
        Generate URL to remove a specific filter while preserving other state.

        :param filter_position: Position of filter to remove in active_filters list
        :param active_filters: List of currently active filters (idx, flt_name, value) tuples
        :param return_url: Base return URL
        :param sort_column: Current sort column index
        :param sort_desc: Whether sort is descending
        :param search: Current search query
        :param page_size: Current page size
        :param default_page_size: Default page size
        :param extra_args: Extra query arguments to preserve
        """
        # Build filter args excluding the one to remove
        # active_filters is a list of (idx, flt_name, value) tuples
        filter_args = {}
        for pos, (idx, flt_name, value) in enumerate(active_filters):
            if pos != filter_position:
                # Reconstruct filter key using the format Flask-Admin expects
                # The key format is: flt{position}_{arg_name}
                # where arg_name comes from get_filter_arg(idx, filter_obj)
                if idx < len(self._filters):
                    filter_obj = self._filters[idx]
                    arg_name = self.get_filter_arg(idx, filter_obj)
                    filter_key = f"flt{pos}_{arg_name}"
                    filter_args[filter_key] = value

        # Build complete URL with all state preserved
        kwargs = {}

        # Add filters
        kwargs.update(filter_args)

        # Add sort
        if sort_column is not None:
            kwargs['sort'] = sort_column
        if sort_desc:
            kwargs['desc'] = 1

        # Add search
        if search:
            kwargs['search'] = search

        # Add page size if not default
        if page_size and page_size != default_page_size:
            kwargs['page_size'] = page_size

        # Add extra args
        if extra_args:
            kwargs.update(extra_args)

        return self.get_url('.index_view', **kwargs)

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
