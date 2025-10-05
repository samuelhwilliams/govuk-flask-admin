"""E2E tests for responsive design."""
import pytest


@pytest.mark.e2e
class TestResponsiveLayout:
    """Test responsive layout at different breakpoints."""

    def test_sidebar_desktop_fixed_width(self, page):
        """Test sidebar is 300px on desktop."""
        page.goto(f"{page.base_url}/admin/user/")
        sidebar = page.locator('.gfa-sidebar-column')
        # TODO: Assert sidebar width is 300px

    def test_sidebar_tablet_width(self, tablet_page):
        """Test sidebar is 260px on tablet."""
        tablet_page.goto(f"{tablet_page.base_url}/admin/user/")
        sidebar = tablet_page.locator('.gfa-sidebar-column')
        # TODO: Assert sidebar width is 260px

    def test_sidebar_mobile_full_width(self, mobile_page):
        """Test sidebar is full width on mobile."""
        mobile_page.goto(f"{mobile_page.base_url}/admin/user/")
        # TODO: Assert sidebar full width or stacked

    def test_table_responsive_mobile(self, mobile_page):
        """Test table is scrollable on mobile."""
        mobile_page.goto(f"{mobile_page.base_url}/admin/user/")
        # TODO: Assert table scrollable or adapted for mobile

    def test_form_stacks_on_mobile(self, mobile_page):
        """Test form fields stack vertically on mobile."""
        mobile_page.goto(f"{mobile_page.base_url}/admin/user/new/")
        # TODO: Assert form fields are stacked

    def test_buttons_full_width_mobile(self, mobile_page):
        """Test buttons are appropriately sized on mobile."""
        mobile_page.goto(f"{mobile_page.base_url}/admin/user/new/")
        # TODO: Assert button sizing appropriate for mobile


@pytest.mark.e2e
class TestViewportChanges:
    """Test behavior when viewport changes."""

    def test_sidebar_adapts_on_resize(self, page):
        """Test sidebar adapts when viewport is resized."""
        page.goto(f"{page.base_url}/admin/user/")
        # TODO: Resize to mobile
        # TODO: Assert sidebar adapted
        # TODO: Resize to desktop
        # TODO: Assert sidebar expanded
