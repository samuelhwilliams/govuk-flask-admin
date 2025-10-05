"""Unit tests for GovukAdminModelConverter."""
import pytest
from govuk_flask_admin import GovukAdminModelConverter
from govuk_frontend_wtf.wtforms_widgets import GovTextInput, GovDateInput


@pytest.mark.unit
class TestGovukAdminModelConverter:
    """Test form field conversion for GOV.UK widgets."""

    def test_maps_string_to_gov_text_input(self, db, user_model_view):
        """Test String columns get GovTextInput widget."""
        # TODO: Test that string fields use GovTextInput

    def test_maps_integer_with_inputmode(self, db, user_model_view):
        """Test Integer columns get numeric inputmode."""
        # TODO: Test that integer fields have inputmode="numeric"

    def test_maps_date_to_gov_date_input(self, db, user_model_view):
        """Test Date columns get GovDateInput widget with correct format."""
        # TODO: Test that date fields use GovDateInput with format "%d %m %Y"

    def test_handles_enum_fields(self, db, user_model_view):
        """Test Enum columns are properly converted."""
        # TODO: Test enum field conversion

    def test_widget_args_inheritance(self, db):
        """Test that widget args from view are merged with defaults."""
        # TODO: Test form_widget_args merging

    def test_field_args_inheritance(self, db):
        """Test that field args from view are merged with defaults."""
        # TODO: Test form_args merging
