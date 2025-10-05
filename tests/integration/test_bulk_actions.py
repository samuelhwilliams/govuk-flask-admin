"""Integration tests for bulk actions."""
import pytest


@pytest.mark.integration
class TestBulkActions:
    """Test bulk action functionality."""

    def test_bulk_action_checkboxes_rendered(self, client, sample_users):
        """Test bulk action checkboxes are present."""
        response = client.get('/admin/user/')
        # TODO: Assert checkboxes with govuk-checkboxes class

    def test_bulk_action_select_all_checkbox(self, client, sample_users):
        """Test select all checkbox is present."""
        response = client.get('/admin/user/')
        # TODO: Assert select-all checkbox present

    def test_bulk_action_dropdown(self, client, sample_users):
        """Test bulk action dropdown is rendered."""
        response = client.get('/admin/user/')
        # TODO: Assert action select dropdown

    def test_bulk_action_requires_selection(self, client, sample_users):
        """Test bulk action requires at least one item selected."""
        response = client.post('/admin/user/action/', data={'action': 'delete'})
        # TODO: Assert error about no selection

    def test_bulk_delete_confirmation_shown(self, client, sample_users):
        """Test bulk delete shows GOV.UK confirmation banner."""
        user_ids = [str(u.id) for u in sample_users[:2]]
        response = client.get(f'/admin/user/?_confirm_action=delete&rowid={user_ids[0]}&rowid={user_ids[1]}')
        # TODO: Assert confirmation banner present
        # TODO: Assert govuk-notification-banner class

    def test_bulk_delete_executes_on_confirmation(self, client, sample_users, db):
        """Test bulk delete executes after confirmation."""
        from tests.conftest import User
        user_ids = [str(u.id) for u in sample_users[:2]]
        data = {
            'action': 'delete',
            'rowid': user_ids,
            'url': '/admin/user/'
        }
        response = client.post('/admin/user/action/', data=data, follow_redirects=True)
        # TODO: Assert users deleted
        # TODO: Assert success message

    def test_bulk_action_cancel(self, client, sample_users):
        """Test cancelling bulk action returns to list."""
        user_ids = [str(u.id) for u in sample_users[:2]]
        response = client.get(f'/admin/user/?_confirm_action=delete&rowid={user_ids[0]}')
        # TODO: Assert cancel link present
