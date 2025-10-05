"""Unit tests for GovukFrontendTheme."""
import pytest
from govuk_flask_admin import GovukFrontendTheme


@pytest.mark.unit
class TestGovukTheme:
    """Test GOV.UK theme configuration."""

    def test_theme_folder(self):
        """Test theme uses correct template folder."""
        theme = GovukFrontendTheme()
        assert theme.folder == "admin"

    def test_theme_base_template(self):
        """Test theme uses correct base template."""
        theme = GovukFrontendTheme()
        assert theme.base_template == "admin/base.html"
