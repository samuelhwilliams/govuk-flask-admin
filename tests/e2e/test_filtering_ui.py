"""E2E tests for filter UI interactions."""
import pytest


@pytest.mark.e2e
class TestFilterInteractions:
    """Test filter UI interactions."""

    def test_filter_details_expands_collapses(self, page):
        """Test clicking filter summary opens/closes filters."""
        page.goto(f"{page.base_url}/admin/user/")
        details = page.locator('details')
        # TODO: Assert details initially closed
        # TODO: Click summary
        # TODO: Assert details opened

    def test_date_filter_three_inputs(self, page):
        """Test date filter shows day/month/year inputs."""
        page.goto(f"{page.base_url}/admin/user/")
        page.click('details summary')  # Open filters
        # TODO: Assert three date inputs present (day, month, year)

    def test_filter_submission_updates_results(self, page):
        """Test submitting filter updates table."""
        page.goto(f"{page.base_url}/admin/user/")
        page.click('details summary')
        # TODO: Fill in filter
        # TODO: Click Apply
        # TODO: Assert table updated
        # TODO: Assert URL contains filter param

    def test_filter_tag_removal(self, page):
        """Test clicking × on filter tag removes filter."""
        page.goto(f"{page.base_url}/admin/user/?flt0_age=25")
        remove_link = page.locator('.gfa-filter-tag-remove')
        # TODO: Click remove link
        # TODO: Assert filter removed
        # TODO: Assert results updated

    def test_clear_all_filters(self, page):
        """Test 'Clear all' link removes all filters."""
        page.goto(f"{page.base_url}/admin/user/?flt0_age=25&search=test")
        clear_link = page.locator('text=Clear all')
        # TODO: Click clear all
        # TODO: Assert all filters removed
        # TODO: Assert search cleared

    def test_enum_filter_dropdown(self, page):
        """Test enum filter shows dropdown with values."""
        page.goto(f"{page.base_url}/admin/user/")
        page.click('details summary')
        # TODO: Locate favourite_colour filter
        # TODO: Assert dropdown has options: red, blue, yellow


@pytest.mark.e2e
class TestFilterPersistence:
    """Test filter state persistence."""

    def test_filters_persist_after_pagination(self, page):
        """Test filters remain after changing page."""
        # TODO: Apply filter
        # TODO: Navigate to page 2
        # TODO: Assert filter still active

    def test_filters_persist_after_sort(self, page):
        """Test filters remain after sorting."""
        # TODO: Apply filter
        # TODO: Sort by column
        # TODO: Assert filter still active
