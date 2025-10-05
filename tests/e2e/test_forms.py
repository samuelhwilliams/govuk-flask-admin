"""E2E tests for form validation and submission."""
import time

import pytest


@pytest.mark.e2e
class TestFormValidation:
    """Test client-side and server-side form validation."""

    def test_required_field_validation(self, page):
        """Test required field validation shows errors."""
        page.goto(f"{page.base_url}/admin/user/new/")
        page.click('input[type="submit"]')

        # Wait for page to reload after submission
        page.wait_for_load_state('networkidle')

        # Assert error messages displayed
        error_messages = page.locator('.govuk-error-message')
        assert error_messages.count() > 0, "Expected error messages to be displayed"

        # Assert GOV.UK error styling
        assert error_messages.first.get_attribute('class') == 'govuk-error-message'

        # Assert fields have error state (form groups should have error class)
        error_form_groups = page.locator('.govuk-form-group--error')
        assert error_form_groups.count() > 0, "Expected form groups to have error class"

    def test_email_validation(self, page):
        """Test email field validates format."""
        page.goto(f"{page.base_url}/admin/user/new/")

        # Fill all required fields except use invalid email format
        page.fill('input[name="email"]', 'invalid-email')
        page.fill('input[name="name"]', 'Test User')
        page.fill('input[name="age"]', '25')
        page.fill('input[name="job"]', 'Tester')
        page.select_option('#favourite_colour', 'RED')
        page.fill('#created_at-day', '15')
        page.fill('#created_at-month', '6')
        page.fill('#created_at-year', '2024')

        page.click('input[type="submit"]')

        # Wait for validation
        page.wait_for_load_state('networkidle')

        # Assert email validation error shown
        email_error = page.locator('#email-error')
        assert email_error.is_visible(), "Expected email format validation error"
        error_text = email_error.text_content()
        assert "email" in error_text.lower() or "invalid" in error_text.lower(), f"Unexpected error text: {error_text}"

    def test_date_input_validation(self, page):
        """Test date input validates day/month/year."""
        page.goto(f"{page.base_url}/admin/user/new/")

        # Fill in invalid date
        page.fill('#created_at-day', '32')
        page.fill('#created_at-month', '13')
        page.fill('#created_at-year', '2024')

        # Fill other required fields to isolate date validation
        page.fill('input[name="email"]', 'test@example.com')
        page.fill('input[name="name"]', 'Test User')
        page.fill('input[name="age"]', '25')
        page.fill('input[name="job"]', 'Tester')
        page.select_option('#favourite_colour', 'RED')

        page.click('input[type="submit"]')

        # Wait for validation
        page.wait_for_load_state('networkidle')

        # Assert validation error (date field should show error)
        # Flask-Admin/WTForms will reject invalid dates
        error_messages = page.locator('.govuk-error-message')
        assert error_messages.count() > 0, "Expected date validation error"

    def test_error_summary(self, page):
        """Test error summary appears at top of form."""
        page.goto(f"{page.base_url}/admin/user/new/")
        page.click('input[type="submit"]')

        # Wait for page reload
        page.wait_for_load_state('networkidle')

        # Assert error summary present
        error_summary = page.locator('.govuk-error-summary')
        assert error_summary.is_visible(), "Expected GOV.UK error summary to be visible"

        # Assert error summary has title
        error_title = page.locator('.govuk-error-summary__title')
        assert error_title.is_visible(), "Expected error summary title"

        # Assert error summary has list of errors
        error_list = page.locator('.govuk-error-summary__list')
        assert error_list.is_visible(), "Expected error summary list"

        # Assert links to fields with errors exist
        error_links = page.locator('.govuk-error-summary__list a')
        assert error_links.count() > 0, "Expected links to fields with errors"


@pytest.mark.e2e
class TestFormSubmission:
    """Test successful form submission."""

    def test_create_form_submission(self, page):
        """Test successful record creation via form."""
        page.goto(f"{page.base_url}/admin/user/new/")

        # Fill in form
        page.fill('input[name="email"]', 'e2e-test@example.com')
        page.fill('input[name="name"]', 'E2E Test User')
        page.fill('input[name="age"]', '30')
        page.fill('input[name="job"]', 'Tester')
        page.select_option('#favourite_colour', 'RED')
        page.fill('#created_at-day', '15')
        page.fill('#created_at-month', '6')
        page.fill('#created_at-year', '2024')

        page.click('input[type="submit"]')

        # TODO: Assert redirected to list view
        # TODO: Assert success message
        # TODO: Assert new record visible

    def test_edit_form_submission(self, page):
        """Test successful record update via form."""
        # TODO: Navigate to edit form
        # TODO: Update fields
        # TODO: Submit
        # TODO: Assert success


@pytest.mark.e2e
class TestFormComponents:
    """Test GOV.UK form components render correctly."""

    def test_govuk_input_classes(self, page):
        """Test text inputs have GOV.UK classes."""
        page.goto(f"{page.base_url}/admin/user/new/")
        inputs = page.locator('.govuk-input')
        # TODO: Assert inputs have correct classes

    def test_govuk_select_classes(self, page):
        """Test select dropdowns have GOV.UK classes."""
        page.goto(f"{page.base_url}/admin/user/new/")
        selects = page.locator('.govuk-select')
        # TODO: Assert selects have correct classes

    def test_govuk_button_classes(self, page):
        """Test buttons have GOV.UK classes."""
        page.goto(f"{page.base_url}/admin/user/new/")
        buttons = page.locator('.govuk-button')
        # TODO: Assert buttons have correct classes
