"""E2E tests for form validation and submission."""
import pytest


@pytest.mark.e2e
class TestFormValidation:
    """Test client-side and server-side form validation."""

    def test_required_field_validation(self, page):
        """Test required field validation shows errors."""
        page.goto(f"{page.base_url}/admin/user/new/")
        page.click('button[type="submit"]')

        # TODO: Assert error messages displayed
        # TODO: Assert GOV.UK error styling (govuk-error-message)
        # TODO: Assert fields have error state

    def test_email_validation(self, page):
        """Test email field validates format."""
        page.goto(f"{page.base_url}/admin/user/new/")
        page.fill('input[name="email"]', 'invalid-email')
        page.click('button[type="submit"]')

        # TODO: Assert email validation error shown

    def test_date_input_validation(self, page):
        """Test date input validates day/month/year."""
        page.goto(f"{page.base_url}/admin/user/new/")
        page.fill('input[name="created_at-day"]', '32')  # Invalid day
        page.click('button[type="submit"]')

        # TODO: Assert validation error

    def test_error_summary(self, page):
        """Test error summary appears at top of form."""
        page.goto(f"{page.base_url}/admin/user/new/")
        page.click('button[type="submit"]')

        # TODO: Assert error summary present
        # TODO: Assert links to fields with errors


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
        page.select_option('select[name="favourite_colour"]', 'RED')
        page.fill('input[name="created_at-day"]', '15')
        page.fill('input[name="created_at-month"]', '6')
        page.fill('input[name="created_at-year"]', '2024')

        page.click('button[type="submit"]')

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
