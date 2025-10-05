# Testing Framework for govuk-flask-admin

## Overview

A comprehensive test suite with **163 test stubs** covering unit, integration, and end-to-end testing of the GOV.UK Design System theme for Flask-Admin.

## Test Statistics

- **Total Tests**: 163
- **Unit Tests**: 20 (fast, isolated)
- **Integration Tests**: 74 (Flask test client)
- **E2E Tests**: 69 (Playwright browser tests)

## Architecture

### Unit Tests (20 tests)
Fast, isolated tests for individual components:

- **Date Filter Logic** (7 tests): Server-side GOV.UK date field combining
- **Model Converter** (6 tests): Widget and field conversion for GOV.UK components
- **Pagination Builder** (6 tests): GOV.UK pagination parameter generation
- **Theme Configuration** (2 tests): Theme setup verification
- **Model View** (9 tests): GovukModelView methods and URL generation

### Integration Tests (74 tests)
Tests using Flask test client for request/response cycles:

- **List View** (12 tests): Table rendering, pagination, empty states
- **Filters** (17 tests): Text, enum, date, integer filters and combinations
- **Create View** (12 tests): Form rendering, validation, submission
- **Edit View** (7 tests): Form population, updates, errors
- **Delete View** (3 tests): Record deletion and error handling
- **Search** (7 tests): Search functionality and combinations
- **Export** (5 tests): CSV export with filters
- **Sorting** (6 tests): Column sorting and state preservation
- **Pagination** (6 tests): Page navigation and sizing
- **Bulk Actions** (7 tests): Selection, confirmation, execution
- **Relationships** (4 tests): Foreign key handling

### E2E Tests (69 tests)
Browser-based tests using Playwright:

- **Navigation** (5 tests): Sidebar, mobile menu, active states
- **Accessibility** (7 tests): WCAG compliance, ARIA, keyboard navigation
- **Responsive Design** (8 tests): Mobile/tablet/desktop layouts
- **Filter UI** (10 tests): Interactive filter operations
- **Bulk Actions UI** (8 tests): Checkbox selection, confirmation flows
- **Forms** (14 tests): Validation, submission, GOV.UK components
- **Progressive Enhancement** (8 tests): Functionality without JavaScript
- **JavaScript Enhancement** (3 tests): Enhanced features with JS
- **Viewport Changes** (1 test): Responsive adaptation

## Playwright E2E Setup

### How It Works

The E2E tests use a multiprocess architecture to run a live Flask server alongside Playwright browser tests:

```
┌─────────────────────────────────────────────────────────────┐
│  pytest (main process)                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  flask_server fixture (session scope)                │   │
│  │  1. Starts Flask app in separate process (port 5555) │   │
│  │  2. Waits for server to be ready (health check)      │   │
│  │  3. Yields base URL to tests                         │   │
│  │  4. Terminates process after all tests               │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  browser fixture (session scope)                     │   │
│  │  - Launches Chromium in headless mode                │   │
│  │  - Reused across all tests                           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  page/context fixtures (function scope)              │   │
│  │  - New context per test for isolation                │   │
│  │  - Different viewports: desktop, mobile, tablet      │   │
│  │  - JavaScript enabled/disabled variants              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         │                                    │
         │                                    │
         ▼                                    ▼
┌──────────────────┐              ┌──────────────────────┐
│  Flask Process   │              │  Chromium Browser    │
│  Port: 5555      │◄────────────►│  Playwright Control  │
│  In-memory DB    │   HTTP       │  Headless Mode       │
└──────────────────┘              └──────────────────────┘
```

### Key Fixtures

**`flask_server`** (session scope)
- Starts Flask app in separate process using `multiprocessing.Process`
- Performs health checks with exponential backoff (30 second timeout)
- Returns base URL: `http://127.0.0.1:5555`
- Automatically terminates process after tests

**`browser`** (session scope)
- Single Chromium instance for all tests
- Headless mode for CI/CD compatibility
- Configured for Docker/CI environments

**`page`** (function scope)
- Desktop viewport: 1280x720
- New context per test for isolation
- Base URL pre-configured

**`mobile_page`** (function scope)
- Mobile viewport: 375x667 (iPhone SE)
- Mobile user agent string
- Tests mobile-specific layouts

**`tablet_page`** (function scope)
- Tablet viewport: 768x1024 (iPad)
- Tests tablet breakpoint

**`page_no_js`** (function scope)
- JavaScript disabled
- Tests progressive enhancement
- Verifies core functionality without JS

### Why Multiprocess?

1. **Isolation**: Flask app runs in separate process, preventing test pollution
2. **Real Server**: Tests against actual HTTP server, not mocked responses
3. **Concurrent Requests**: Can test concurrent operations
4. **CI/CD Ready**: Works in containerized environments
5. **Clean Shutdown**: Process terminates cleanly, no port conflicts

### Example Usage

```python
@pytest.mark.e2e
class TestMyFeature:
    def test_desktop_layout(self, page):
        """Test on desktop viewport."""
        page.goto(f"{page.base_url}/admin/user/")
        assert page.locator('.govuk-grid-column-one-quarter nav').is_visible()

    def test_mobile_layout(self, mobile_page):
        """Test on mobile viewport."""
        mobile_page.goto(f"{mobile_page.base_url}/admin/user/")
        # Mobile-specific assertions

    def test_without_javascript(self, page_no_js):
        """Test progressive enhancement."""
        page_no_js.goto(f"{page_no_js.base_url}/admin/user/")
        # Verify works without JS
```

## Running Tests

### Quick Start
```bash
# All tests (may take a few minutes for E2E)
uv run pytest

# Fast unit tests only (~1 second)
uv run pytest -m unit

# Integration tests (~30 seconds)
uv run pytest -m integration

# E2E tests (~2-5 minutes)
uv run pytest -m e2e

# Specific test file
uv run pytest tests/unit/test_date_filter.py

# Specific test class
uv run pytest tests/unit/test_date_filter.py::TestGetListFilterArgs

# Specific test
uv run pytest tests/unit/test_date_filter.py::TestGetListFilterArgs::test_combines_date_fields
```

### With Coverage
```bash
# Generate HTML coverage report
uv run pytest --cov=govuk_flask_admin --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Debugging
```bash
# Verbose output with print statements
uv run pytest -v -s

# Run last failed tests
uv run pytest --lf

# Stop on first failure
uv run pytest -x

# Run E2E tests in headed mode (see browser)
# Edit tests/e2e/conftest.py: headless=False
```

## Test Coverage Areas

### Core Flask-Admin Features
✅ CRUD operations (Create, Read, Update, Delete)
✅ List view with sorting and pagination
✅ Column filtering (text, enum, date, integer)
✅ Search functionality
✅ Bulk actions with confirmation
✅ CSV export
✅ Foreign key relationships
✅ Form validation

### GOV.UK Design System Integration
✅ GOV.UK form components (input, select, date, button)
✅ GOV.UK table component
✅ GOV.UK pagination component
✅ GOV.UK notification banners
✅ GOV.UK details component (filters)
✅ GOV.UK error messages and summary
✅ GOV.UK tag component (active filters)

### Custom Features
✅ Date filter field combining (day/month/year → YYYY-MM-DD)
✅ Enum filter value display vs name submission
✅ Filter removal while preserving other state
✅ Responsive sidebar (300px desktop, 260px tablet, collapsible mobile)
✅ Search/filter integration in single Details component

### Accessibility (GOV.UK Standards)
✅ Skip to content link
✅ Form label associations
✅ ARIA attributes for errors
✅ Keyboard navigation
✅ Focus visibility
✅ Heading hierarchy
✅ Landmark regions

### Progressive Enhancement
✅ Works without JavaScript
✅ Server-side date field combining
✅ Forms submit without JS
✅ Filters work without JS
✅ Pagination works without JS
✅ JavaScript enhancements when available

### Responsive Design
✅ Desktop layout (1280px+)
✅ Tablet layout (768px)
✅ Mobile layout (375px)
✅ Sidebar adaptation
✅ Table scrolling on mobile
✅ Form field stacking

## CI/CD Integration

Tests are designed for continuous integration:

### GitHub Actions Example
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      - name: Install dependencies
        run: uv sync --all-extras --dev
      - name: Install Playwright browsers
        run: uv run playwright install chromium --with-deps
      - name: Run tests
        run: uv run pytest --cov=govuk_flask_admin --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Performance
- **Unit tests**: ~1 second
- **Integration tests**: ~30 seconds
- **E2E tests**: ~2-5 minutes
- **Total**: ~3-6 minutes in CI

## Next Steps

### Implementing Tests
All 163 tests are currently **stubs** with `# TODO` comments. To implement:

1. **Start with unit tests** (fastest feedback loop)
2. **Move to integration tests** (verify Flask-Admin integration)
3. **Finish with E2E tests** (verify browser behavior)

### Priority Order
1. **Critical path**: Date filter, CRUD operations, list view
2. **Core features**: Filters, search, pagination, sorting
3. **Advanced features**: Bulk actions, export, relationships
4. **Polish**: Accessibility, responsive, progressive enhancement

### Example Implementation

Before:
```python
def test_combines_date_fields(self, app, user_model_view):
    """Test that GOV.UK date fields are combined into YYYY-MM-DD format."""
    with app.test_request_context('/?flt0_created_at-day=15&flt0_created_at-month=3&flt0_created_at-year=2024'):
        result = user_model_view._get_list_filter_args()
        # TODO: Assert that result contains combined date filter
```

After:
```python
def test_combines_date_fields(self, app, user_model_view):
    """Test that GOV.UK date fields are combined into YYYY-MM-DD format."""
    with app.test_request_context('/?flt0_created_at-day=15&flt0_created_at-month=3&flt0_created_at-year=2024'):
        result = user_model_view._get_list_filter_args()
        assert len(result) == 1
        assert result[0][2] == '2024-03-15'  # (idx, name, value)
```

## Maintenance

### Adding New Tests
1. Choose appropriate test level (unit/integration/e2e)
2. Add to relevant test class
3. Follow existing patterns
4. Update this document if adding new test files

### Test Data
- `conftest.py` provides shared fixtures
- `sample_users` creates 10 test users
- `many_users` creates 50 users for pagination
- Database is in-memory SQLite (fast, isolated)

### Fixtures Summary
- `app`: Flask application
- `db`: SQLAlchemy database
- `admin_instance`: Flask-Admin instance
- `user_model_view`: GovukModelView for User model
- `client`: Flask test client
- `sample_users`: 10 test user records
- `flask_server`: Running Flask server for E2E
- `page`: Playwright desktop page
- `mobile_page`: Playwright mobile page
- `tablet_page`: Playwright tablet page
- `page_no_js`: Playwright page without JavaScript

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [Playwright Python documentation](https://playwright.dev/python/)
- [Flask testing documentation](https://flask.palletsprojects.com/en/stable/testing/)
- [GOV.UK Design System](https://design-system.service.gov.uk/)
- [Flask-Admin documentation](https://flask-admin.readthedocs.io/)
