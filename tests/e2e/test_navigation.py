"""E2E tests for navigation and sidebar."""
import pytest


@pytest.mark.e2e
class TestSidebarNavigation:
    """Test sidebar navigation functionality."""

    def test_sidebar_visible_on_desktop(self, page):
        """Test sidebar is visible on desktop viewport."""
        page.goto(f"{page.base_url}/admin/user/")
        sidebar = page.locator('.gfa-sidebar')
        # TODO: Assert sidebar is visible

    def test_sidebar_links_functional(self, page):
        """Test sidebar links navigate correctly."""
        page.goto(f"{page.base_url}/admin/")
        # TODO: Click sidebar link
        # TODO: Assert navigation occurred

    def test_active_menu_item_highlighted(self, page):
        """Test current page highlighted in sidebar."""
        page.goto(f"{page.base_url}/admin/user/")
        # TODO: Assert active class on current menu item


@pytest.mark.e2e
class TestMobileNavigation:
    """Test navigation on mobile devices."""

    def test_sidebar_collapsible_on_mobile(self, mobile_page):
        """Test sidebar can be toggled on mobile."""
        mobile_page.goto(f"{mobile_page.base_url}/admin/user/")
        # TODO: Assert sidebar initially collapsed/at top
        # TODO: Click menu button
        # TODO: Assert sidebar expanded

    def test_menu_button_visible_mobile(self, mobile_page):
        """Test menu toggle button visible on mobile."""
        mobile_page.goto(f"{mobile_page.base_url}/admin/user/")
        # TODO: Assert toggle button visible
