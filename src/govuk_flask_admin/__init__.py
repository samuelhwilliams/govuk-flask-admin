import glob
import os
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent

from flask import Flask, Blueprint, url_for, send_from_directory
from flask_admin.theme import Theme


ROOT_DIR = Path(__file__).parent


@dataclass
class GovukFrontendV5_6Theme(Theme):
    folder: str = 'admin'
    base_template: str = 'admin/base.html'


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

    def static(
        self, filename, vite_routes_host: str | None = None  # noqa: ARG002
    ):
        dist = str(ROOT_DIR / "static" / "govuk-frontend")
        return send_from_directory(dist, filename, max_age=60 * 60 * 24 * 7 * 52)
