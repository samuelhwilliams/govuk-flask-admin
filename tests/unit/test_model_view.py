"""Unit tests for GovukModelView."""
import pytest
from govuk_flask_admin import GovukModelView


@pytest.mark.unit
class TestGovukModelView:
    """Test GovukModelView configuration and methods."""

    def test_default_category(self, db):
        """Test that default category is set to 'Miscellaneous'."""
        from tests.conftest import User
        view = GovukModelView(User, db.session)
        assert view.category == "Miscellaneous"

    def test_custom_category(self, db):
        """Test that custom category can be set."""
        from tests.conftest import User
        view = GovukModelView(User, db.session, category="Custom")
        assert view.category == "Custom"

    def test_uses_govuk_converter(self, db):
        """Test that GovukAdminModelConverter is used."""
        from tests.conftest import User
        from govuk_flask_admin import GovukAdminModelConverter
        view = GovukModelView(User, db.session)
        assert view.model_form_converter == GovukAdminModelConverter


@pytest.mark.unit
class TestGetRemoveFilterUrl:
    """Test GovukModelView._get_remove_filter_url() method."""

    def test_removes_specified_filter(self, app, user_model_view):
        """Test that specified filter is removed from URL."""
        # TODO: Test filter removal

    def test_preserves_other_filters(self, app, user_model_view):
        """Test that other filters remain in URL."""
        # TODO: Test other filters preserved

    def test_preserves_sort_state(self, app, user_model_view):
        """Test that sort column and direction are preserved."""
        # TODO: Test sort preservation

    def test_preserves_search(self, app, user_model_view):
        """Test that search query is preserved."""
        # TODO: Test search preservation

    def test_preserves_page_size(self, app, user_model_view):
        """Test that non-default page size is preserved."""
        # TODO: Test page size preservation

    def test_preserves_extra_args(self, app, user_model_view):
        """Test that extra query arguments are preserved."""
        # TODO: Test extra args preservation
