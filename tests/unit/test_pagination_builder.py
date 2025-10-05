"""Unit tests for GOV.UK pagination helper."""
import pytest
from govuk_flask_admin import govuk_pagination_params_builder


@pytest.mark.unit
class TestPaginationBuilder:
    """Test govuk_pagination_params_builder function."""

    def test_first_page(self):
        """Test pagination params for page 0."""
        def url_gen(page):
            return f"/?page={page}"

        result = govuk_pagination_params_builder(0, 5, url_gen)
        # TODO: Assert no 'previous' link
        # TODO: Assert 'next' link exists
        # TODO: Assert page 1 is current

    def test_last_page(self):
        """Test pagination params for last page."""
        def url_gen(page):
            return f"/?page={page}"

        result = govuk_pagination_params_builder(4, 5, url_gen)
        # TODO: Assert 'previous' link exists
        # TODO: Assert no 'next' link
        # TODO: Assert page 5 is current

    def test_middle_page_with_ellipsis(self):
        """Test pagination params with ellipsis for many pages."""
        def url_gen(page):
            return f"/?page={page}"

        result = govuk_pagination_params_builder(5, 10, url_gen)
        # TODO: Assert ellipsis items present
        # TODO: Assert page 6 is current (0-indexed becomes 1-indexed)

    def test_three_pages_or_less_no_ellipsis(self):
        """Test pagination without ellipsis for small page counts."""
        def url_gen(page):
            return f"/?page={page}"

        result = govuk_pagination_params_builder(1, 3, url_gen)
        # TODO: Assert no ellipsis
        # TODO: Assert all 3 pages shown

    def test_includes_govuk_classes(self):
        """Test that GOV.UK classes are added to pagination."""
        def url_gen(page):
            return f"/?page={page}"

        result = govuk_pagination_params_builder(0, 2, url_gen)
        # TODO: Assert 'govuk-!-text-align-center' class present

    def test_single_page(self):
        """Test pagination with only one page."""
        def url_gen(page):
            return f"/?page={page}"

        result = govuk_pagination_params_builder(0, 1, url_gen)
        # TODO: Assert no previous/next links
        # TODO: Assert single page shown
