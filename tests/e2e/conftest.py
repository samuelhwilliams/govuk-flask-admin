"""Playwright fixtures for e2e tests."""
import pytest
import multiprocessing
import time
import requests
from playwright.sync_api import sync_playwright


def run_flask_app(port):
    """Run Flask app in separate process for e2e tests."""
    import sys
    import os

    # Add project root to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

    from app import app

    # Configure for testing
    app.config['TESTING'] = True

    # Run the app
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)


@pytest.fixture(scope="session")
def flask_server():
    """Start Flask server in separate process for e2e tests.

    This fixture:
    1. Starts the Flask app in a separate process
    2. Waits for it to be ready
    3. Yields the base URL
    4. Terminates the process after tests complete
    """
    port = 5555
    base_url = f"http://127.0.0.1:{port}"

    # Start Flask in separate process
    process = multiprocessing.Process(
        target=run_flask_app,
        args=(port,),
        daemon=True
    )
    process.start()

    # Wait for server to be ready (max 30 seconds)
    for _ in range(30):
        try:
            response = requests.get(base_url, timeout=1)
            if response.status_code:
                break
        except (requests.ConnectionError, requests.Timeout):
            time.sleep(1)
    else:
        process.terminate()
        raise RuntimeError("Flask server failed to start within 30 seconds")

    yield base_url

    # Cleanup
    process.terminate()
    process.join(timeout=5)
    if process.is_alive():
        process.kill()


@pytest.fixture(scope="session")
def playwright_instance():
    """Create Playwright instance for session."""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance):
    """Create browser instance for session."""
    browser = playwright_instance.chromium.launch(
        headless=True,
        args=['--disable-dev-shm-usage']  # Helps with Docker/CI environments
    )
    yield browser
    browser.close()


@pytest.fixture
def context(browser):
    """Create new browser context for each test."""
    context = browser.new_context(
        viewport={'width': 1280, 'height': 720},
        locale='en-GB',
    )
    yield context
    context.close()


@pytest.fixture
def page(context, flask_server):
    """Create new page for each test with base URL configured."""
    page = context.new_page()
    page.base_url = flask_server
    yield page
    page.close()


@pytest.fixture
def mobile_page(browser, flask_server):
    """Create page with mobile viewport."""
    context = browser.new_context(
        viewport={'width': 375, 'height': 667},  # iPhone SE size
        user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
    )
    page = context.new_page()
    page.base_url = flask_server
    yield page
    context.close()


@pytest.fixture
def tablet_page(browser, flask_server):
    """Create page with tablet viewport."""
    context = browser.new_context(
        viewport={'width': 768, 'height': 1024},  # iPad size
    )
    page = context.new_page()
    page.base_url = flask_server
    yield page
    context.close()
