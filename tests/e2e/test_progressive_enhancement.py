"""E2E tests for progressive enhancement (functionality without JavaScript)."""
import pytest


@pytest.mark.e2e
class TestNoJavaScript:
    """Test functionality works without JavaScript."""

    @pytest.fixture
    def page_no_js(self, browser, flask_server):
        """Create page with JavaScript disabled."""
        context = browser.new_context(
            java_script_enabled=False,
            viewport={'width': 1280, 'height': 720}
        )
        page = context.new_page()
        page.base_url = flask_server
        yield page
        context.close()

    def test_sidebar_visible_without_js(self, page_no_js):
        """Test sidebar is visible when JS disabled."""
        page_no_js.goto(f"{page_no_js.base_url}/admin/user/")
        sidebar = page_no_js.locator('.gfa-sidebar')
        # TODO: Assert sidebar visible

    def test_forms_submit_without_js(self, page_no_js):
        """Test forms work without JavaScript."""
        page_no_js.goto(f"{page_no_js.base_url}/admin/user/new/")

        # Fill and submit form
        page_no_js.fill('input[name="email"]', 'nojs@example.com')
        page_no_js.fill('input[name="name"]', 'No JS User')
        page_no_js.fill('input[name="age"]', '25')
        page_no_js.fill('input[name="job"]', 'Tester')
        page_no_js.select_option('select[name="favourite_colour"]', 'RED')
        page_no_js.fill('input[id="created_at-day"]', '1')
        page_no_js.fill('input[id="created_at-month"]', '1')
        page_no_js.fill('input[id="created_at-year"]', '2024')

        page_no_js.click('input[type="submit"]')

        # TODO: Assert form submission worked

    def test_date_filter_works_without_js(self, page_no_js):
        """Test date filter combines fields server-side without JS."""
        page_no_js.goto(f"{page_no_js.base_url}/admin/user/")

        # Open filter details (should work without JS)
        # Fill date filter
        # Submit
        # TODO: Assert filter applied correctly

    def test_pagination_works_without_js(self, page_no_js):
        """Test pagination links work without JavaScript."""
        page_no_js.goto(f"{page_no_js.base_url}/admin/user/")
        # TODO: Click pagination link
        # TODO: Assert page changed

    def test_sorting_works_without_js(self, page_no_js):
        """Test column sorting works without JavaScript."""
        page_no_js.goto(f"{page_no_js.base_url}/admin/user/")
        # TODO: Click sort link
        # TODO: Assert results sorted

    def test_search_works_without_js(self, page_no_js):
        """Test search works without JavaScript."""
        page_no_js.goto(f"{page_no_js.base_url}/admin/user/")
        # TODO: Fill search
        # TODO: Submit
        # TODO: Assert search applied


@pytest.mark.e2e
class TestJavaScriptEnhancement:
    """Test JavaScript enhancements when available."""

    def test_select_all_checkbox_requires_js(self, page):
        """Test select all checkbox functionality (requires JS)."""
        page.goto(f"{page.base_url}/admin/user/")
        # TODO: Test select all functionality

    def test_selected_count_updates_with_js(self, page):
        """Test selected count updates dynamically (requires JS)."""
        page.goto(f"{page.base_url}/admin/user/")
        # TODO: Test count updates on checkbox change

    def test_filter_empty_field_removal(self, page):
        """Test empty filter fields removed before submit (JS enhancement)."""
        page.goto(f"{page.base_url}/admin/user/")
        # TODO: Test that empty fields don't appear in URL
