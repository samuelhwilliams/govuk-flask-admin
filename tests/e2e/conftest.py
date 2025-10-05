"""Playwright fixtures for e2e tests."""
import pytest
from playwright.sync_api import sync_playwright
import subprocess
import time
import requests
import sys


@pytest.fixture(scope="session")
def flask_server():
    """Start Flask server in separate process for e2e tests.

    Uses subprocess instead of pytest-flask's live_server to avoid
    async event loop conflicts with Playwright during teardown.

    Note: Does not depend on app/db/admin_instance fixtures to avoid
    Flask context teardown issues.
    """
    port = 5555  # Use fixed port for testing

    # Create a simple runner script
    runner_code = f"""
import sys
sys.path.insert(0, '{sys.path[0]}')
from app import _create_app

app, admin, db = _create_app(config_overrides={{
    'TESTING': True,
    'SQLALCHEMY_ENGINES': {{'default': 'sqlite:///:memory:'}},
}})
app.run(host='127.0.0.1', port={port}, debug=False, use_reloader=False)
"""

    # Start server in subprocess
    server_process = subprocess.Popen(
        [sys.executable, '-c', runner_code],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for server to be ready
    base_url = f"http://127.0.0.1:{port}"
    for _ in range(50):  # Try for 5 seconds
        try:
            requests.get(f"{base_url}/admin/", timeout=1)
            break
        except (requests.ConnectionError, requests.Timeout):
            time.sleep(0.1)
    else:
        stdout, stderr = server_process.communicate(timeout=1)
        server_process.kill()
        raise RuntimeError(f"Flask server failed to start. stderr: {stderr.decode()}")

    yield base_url

    # Cleanup
    server_process.terminate()
    try:
        server_process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        server_process.kill()


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
