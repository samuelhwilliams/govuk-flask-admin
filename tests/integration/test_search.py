"""Integration tests for search functionality."""
import pytest


@pytest.mark.integration
class TestSearch:
    """Test search functionality."""

    def test_search_input_rendered(self, client, sample_users):
        """Test search input is displayed."""
        response = client.get('/admin/user/')
        # TODO: Assert search input present

    def test_search_by_email(self, client, sample_users):
        """Test searching by email."""
        response = client.get('/admin/user/?search=user0@example.com')
        # TODO: Assert only matching user shown

    def test_search_by_name(self, client, sample_users):
        """Test searching by name."""
        response = client.get('/admin/user/?search=User 0')
        # TODO: Assert only matching user shown

    def test_search_partial_match(self, client, sample_users):
        """Test search with partial matches."""
        response = client.get('/admin/user/?search=user')
        # TODO: Assert all users shown (all match)

    def test_search_no_results(self, client, sample_users):
        """Test search with no matching results."""
        response = client.get('/admin/user/?search=nonexistent')
        # TODO: Assert empty message shown

    def test_search_combined_with_filters(self, client, sample_users):
        """Test search works alongside filters."""
        response = client.get('/admin/user/?search=user&flt0_age=20')
        # TODO: Assert both search and filter applied

    def test_clear_search_link(self, client, sample_users):
        """Test 'Clear all' link clears search."""
        response = client.get('/admin/user/?search=test')
        # TODO: Assert clear link present
