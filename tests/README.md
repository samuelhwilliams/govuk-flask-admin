# Test Suite for govuk-flask-admin

This test suite provides comprehensive coverage of the GOV.UK Design System theme for Flask-Admin.

## Test Structure

```
tests/
├── conftest.py                    # Shared pytest fixtures
├── unit/                          # Unit tests (fast, isolated)
│   ├── test_converter.py          # Form field converter tests
│   ├── test_model_view.py         # GovukModelView tests
│   ├── test_theme.py              # Theme configuration tests
│   ├── test_pagination.py         # Pagination helper tests
│   └── test_date_filter.py        # Date filter logic tests
├── integration/                   # Integration tests (Flask test client)
│   ├── test_list_view.py          # List view functionality
│   ├── test_create_view.py        # Create functionality
│   ├── test_edit_view.py          # Edit functionality
│   ├── test_delete_view.py        # Delete functionality
│   ├── test_filters.py            # All filter types
│   ├── test_search.py             # Search functionality
│   ├── test_export.py             # CSV export
│   ├── test_pagination.py         # Pagination integration
│   ├── test_sorting.py            # Column sorting
│   ├── test_bulk_actions.py       # Bulk actions
│   └── test_relationships.py      # Foreign key relationships
└── e2e/                           # End-to-end browser tests (Playwright)
    ├── conftest.py                # Playwright fixtures
    ├── test_navigation.py         # Sidebar and navigation
    ├── test_accessibility.py      # GOV.UK accessibility
    ├── test_responsive.py         # Responsive layouts
    ├── test_filtering_ui.py       # Filter UI interactions
    ├── test_bulk_actions_ui.py    # Bulk action workflows
    ├── test_forms.py              # Form validation
    └── test_progressive_enhancement.py  # JS disabled scenarios
```

## Running Tests

### All tests
```bash
uv run pytest
```

### Unit tests only (fast)
```bash
uv run pytest -m unit
```

### Integration tests only
```bash
uv run pytest -m integration
```

### E2E tests only (slower, requires browser)
```bash
uv run pytest -m e2e
```

### With coverage report
```bash
uv run pytest --cov=govuk_flask_admin --cov-report=html
```

### Run specific test file
```bash
uv run pytest tests/unit/test_date_filter.py
```

### Run specific test class
```bash
uv run pytest tests/unit/test_date_filter.py::TestGetListFilterArgs
```

### Run specific test method
```bash
uv run pytest tests/unit/test_date_filter.py::TestGetListFilterArgs::test_combines_date_fields
```

## E2E Test Setup

The E2E tests use Playwright to run browser-based tests. The setup:

1. **Multiprocess Architecture**: A separate Python process runs the Flask app on port 5555
2. **Automatic Startup**: The `flask_server` fixture starts the server and waits for it to be ready
3. **Automatic Cleanup**: The server process is terminated after all tests complete
4. **Browser Management**: Playwright manages Chromium browser instances

### How it works:

```python
# tests/e2e/conftest.py contains:

@pytest.fixture(scope="session")
def flask_server():
    """Starts Flask app in separate process"""
    process = multiprocessing.Process(target=run_flask_app, args=(5555,))
    process.start()

    # Wait for server to be ready
    for _ in range(30):
        try:
            requests.get("http://127.0.0.1:5555")
            break
        except requests.ConnectionError:
            time.sleep(1)

    yield "http://127.0.0.1:5555"

    process.terminate()
```

The fixtures provide:
- `flask_server`: Base URL of running Flask app
- `page`: Desktop browser page
- `mobile_page`: Mobile viewport (375x667)
- `tablet_page`: Tablet viewport (768x1024)
- `page_no_js`: Page with JavaScript disabled

## Test Coverage Areas

### Unit Tests
- Date filter field combining logic
- Form field widget conversion
- Pagination parameter building
- Theme configuration
- Filter URL generation

### Integration Tests
- List view rendering (table, pagination, etc.)
- Create/Edit/Delete operations
- All filter types (text, enum, date, integer)
- Search functionality
- CSV export
- Column sorting
- Bulk actions with confirmation
- Foreign key relationships

### E2E Tests
- Sidebar navigation (desktop/mobile)
- GOV.UK accessibility compliance
- Responsive design (mobile/tablet/desktop)
- Filter UI interactions
- Bulk action workflows
- Form validation and submission
- Progressive enhancement (works without JS)

## Writing New Tests

### Unit Test Example
```python
@pytest.mark.unit
class TestMyFeature:
    """Test my new feature."""

    def test_something(self, app, user_model_view):
        """Test something specific."""
        # Arrange
        # Act
        # Assert
```

### Integration Test Example
```python
@pytest.mark.integration
class TestMyView:
    """Test my view integration."""

    def test_view_works(self, client, sample_users):
        """Test view functionality."""
        response = client.get('/admin/myview/')
        assert response.status_code == 200
```

### E2E Test Example
```python
@pytest.mark.e2e
class TestMyUIFeature:
    """Test UI interaction."""

    def test_user_can_do_something(self, page):
        """Test user interaction."""
        page.goto(f"{page.base_url}/admin/user/")
        page.click('button.my-button')
        assert page.locator('.result').is_visible()
```

## Continuous Integration

These tests are designed to run in CI environments:

- Unit tests: ~seconds
- Integration tests: ~30 seconds
- E2E tests: ~2-5 minutes

Playwright is configured for headless mode and works in Docker/CI environments.

## Debugging

### Run tests with output
```bash
uv run pytest -v -s
```

### Debug specific test
```bash
uv run pytest tests/unit/test_date_filter.py::TestGetListFilterArgs::test_combines_date_fields -v -s
```

### Run E2E tests in headed mode (see browser)
Modify `tests/e2e/conftest.py` to set `headless=False` in browser fixture.

### Playwright trace/screenshots
```python
# In test:
page.screenshot(path="debug.png")
```
