"""E2E tests for bulk action UI interactions."""
import pytest
from playwright.sync_api import expect


@pytest.mark.e2e
class TestBulkActionUI:
    """Test bulk action user interactions."""

    def test_select_all_checkbox_toggles_all(self, page):
        """Test select all checkbox selects/deselects all rows."""
        page.goto(f"{page.base_url}/admin/user/")
        page.wait_for_selector('.govuk-table')

        select_all = page.locator('#select-all')
        checkboxes = page.locator('.action-checkbox')

        # Initially all unchecked
        assert select_all.is_checked() == False
        for i in range(checkboxes.count()):
            assert checkboxes.nth(i).is_checked() == False

        # Click select all
        select_all.check()

        # All should be checked
        assert select_all.is_checked() == True
        for i in range(checkboxes.count()):
            assert checkboxes.nth(i).is_checked() == True

        # Click select all again to uncheck
        select_all.uncheck()

        # All should be unchecked
        assert select_all.is_checked() == False
        for i in range(checkboxes.count()):
            assert checkboxes.nth(i).is_checked() == False

    def test_selected_count_updates(self, page):
        """Test selected count updates as checkboxes change."""
        page.goto(f"{page.base_url}/admin/user/")
        page.wait_for_selector('.govuk-table')

        # Open the actions menu to see the delete button
        actions_menu_button = page.locator('.moj-button-menu__toggle-button')
        checkboxes = page.locator('.action-checkbox')

        # Check initial state - open menu and check button text
        actions_menu_button.click()
        delete_button = page.locator('button[form="bulk-action-form"][value="delete"]')
        assert "(0 selected)" in delete_button.text_content()
        actions_menu_button.click()  # Close menu

        # Check first checkbox
        checkboxes.first.check()
        page.wait_for_timeout(100)  # Wait for JavaScript to update
        actions_menu_button.click()
        assert "(1 selected)" in delete_button.text_content()
        actions_menu_button.click()

        # Check second checkbox
        checkboxes.nth(1).check()
        page.wait_for_timeout(100)
        actions_menu_button.click()
        assert "(2 selected)" in delete_button.text_content()
        actions_menu_button.click()

        # Uncheck first checkbox
        checkboxes.first.uncheck()
        page.wait_for_timeout(100)
        actions_menu_button.click()
        assert "(1 selected)" in delete_button.text_content()
        actions_menu_button.click()

    def test_bulk_action_confirmation_flow(self, page):
        """Test full bulk action workflow with confirmation."""
        page.goto(f"{page.base_url}/admin/account/")

        # Get initial row count (should be 8 from seed_database)
        expect(page.locator('p', has_text='Showing 8 results')).to_be_visible()

        # Select first two checkboxes
        checkboxes = page.locator('.action-checkbox')
        checkboxes.first.check()
        checkboxes.nth(1).check()

        # Open actions menu and click delete
        actions_menu_button = page.locator('.moj-button-menu__toggle-button')
        actions_menu_button.click()
        delete_button = page.locator('button[form="bulk-action-form"][value="delete"]')
        delete_button.click()

        # Should redirect to confirmation page
        page.wait_for_selector('.govuk-notification-banner--important')

        # Assert confirmation banner shown
        confirmation = page.locator('.govuk-notification-banner--important')
        assert confirmation.is_visible()
        assert "Confirm" in confirmation.text_content()
        assert "2 item(s) selected" in confirmation.text_content()

        # Click confirm button
        confirm_button = page.locator('button:has-text("Confirm")')
        confirm_button.click()

        # Wait for redirect back to list
        page.wait_for_load_state('networkidle')
        page.wait_for_selector('.govuk-table')

        # Assert success message
        success_banner = page.locator('.govuk-notification-banner--success')
        assert success_banner.is_visible(), "Expected success notification banner"

        expect(page.locator('p', has_text='Showing 6 results')).to_be_visible()

    def test_bulk_action_validation(self, page):
        """Test bulk action requires selection and action choice."""
        page.goto(f"{page.base_url}/admin/user/")
        page.wait_for_selector('.govuk-table')

        # Set up dialog handler to capture alert
        alerts = []
        def handle_dialog(dialog):
            alerts.append(dialog.message)
            dialog.accept()

        page.on("dialog", handle_dialog)

        # Verify button shows 0 selected when no items are selected
        actions_menu_button = page.locator('.moj-button-menu__toggle-button')
        actions_menu_button.click()
        delete_button = page.locator('button[form="bulk-action-form"][value="delete"]')

        # Button should show (0 selected) when no items selected
        assert "(0 selected)" in delete_button.text_content()

        actions_menu_button.click()  # Close menu

        checkboxes = page.locator('.action-checkbox')
        checkboxes.first.check()
        page.wait_for_timeout(100)

        # Verify count updates after selection
        actions_menu_button.click()
        assert "(1 selected)" in delete_button.text_content()

    def test_bulk_action_cancel(self, page):
        """Test cancelling bulk action."""
        page.goto(f"{page.base_url}/admin/user/")
        page.wait_for_selector('.govuk-table')

        # Get initial row count
        initial_rows = page.locator('.govuk-table__body .govuk-table__row').count()

        # Select first two checkboxes
        checkboxes = page.locator('.action-checkbox')
        checkboxes.first.check()
        checkboxes.nth(1).check()

        # Open actions menu and click delete
        actions_menu_button = page.locator('.moj-button-menu__toggle-button')
        actions_menu_button.click()
        delete_button = page.locator('button[form="bulk-action-form"][value="delete"]')
        delete_button.click()

        # Wait for confirmation page
        page.wait_for_selector('.govuk-notification-banner--important')

        # Click cancel link
        cancel_link = page.locator('a:has-text("Cancel")')
        cancel_link.click()

        # Assert returned to list view (no confirmation banner)
        page.wait_for_selector('.govuk-table')
        assert page.locator('.govuk-notification-banner--important').count() == 0

        # Assert records not deleted (same row count)
        final_rows = page.locator('.govuk-table__body .govuk-table__row').count()
        assert final_rows == initial_rows


@pytest.mark.e2e
class TestBulkActionAccessibility:
    """Test bulk action accessibility."""

    def test_checkboxes_have_labels(self, page):
        """Test all checkboxes have accessible labels."""
        page.goto(f"{page.base_url}/admin/user/")
        page.wait_for_selector('.govuk-table')

        checkboxes = page.locator('.action-checkbox')

        # Each checkbox should have an associated label
        for i in range(checkboxes.count()):
            checkbox = checkboxes.nth(i)
            checkbox_id = checkbox.get_attribute('id')

            # Find label with for attribute matching checkbox id
            label = page.locator(f'label[for="{checkbox_id}"]')
            assert label.count() > 0, f"Checkbox {checkbox_id} has no associated label"

            # Check aria-label as fallback
            aria_label = checkbox.get_attribute('aria-label')
            assert aria_label or label.count() > 0, f"Checkbox {checkbox_id} has no label or aria-label"

    def test_select_all_has_label(self, page):
        """Test select all checkbox has label."""
        page.goto(f"{page.base_url}/admin/user/")
        page.wait_for_selector('.govuk-table')

        select_all = page.locator('#select-all')

        # Should have associated label
        label = page.locator('label[for="select-all"]')
        assert label.count() > 0

        # Check aria-label as well
        aria_label = select_all.get_attribute('aria-label')
        assert aria_label or label.count() > 0
