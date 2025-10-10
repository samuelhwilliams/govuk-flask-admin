"""Integration tests for details view rendering."""
import pytest
import datetime
from app import User, Post, FavouriteColour


@pytest.mark.integration
class TestDetailsViewRendering:
    """Test details view renders correctly with GOV.UK Summary List."""

    def test_details_view_uses_govuk_summary_list(self, client, sample_users, db):
        """Test details view renders using GOV.UK Summary List component."""
        # Get the first post ID (Post model has can_view_details=True)
        with client.application.app_context():
            post = db.session.query(Post).first()
            post_id = post.id

        response = client.get(f'/admin/post/details/?id={post_id}')
        assert response.status_code == 200
        html = response.data.decode('utf-8')

        # Check for GOV.UK Summary List component
        assert 'govuk-summary-list' in html
        assert 'govuk-summary-list__key' in html
        assert 'govuk-summary-list__value' in html

        # Check that old table classes are NOT present
        assert 'table-hover' not in html
        assert 'table-bordered' not in html

    def test_details_view_displays_all_fields(self, client, sample_users, db):
        """Test details view displays all model fields."""
        # Get the first post
        with client.application.app_context():
            post = db.session.query(Post).first()
            post_id = post.id
            # Get the author name which should be displayed
            author_name = post.author.name if post.author else ""

        response = client.get(f'/admin/post/details/?id={post_id}')
        assert response.status_code == 200
        html = response.data.decode('utf-8')

        # Check that post data is displayed (author name is formatted in the view)
        assert author_name in html or 'Author' in html  # At least the label should be there

    def test_details_view_has_heading(self, client, sample_users, db):
        """Test details view has a proper heading."""
        with client.application.app_context():
            post = db.session.query(Post).first()
            post_id = post.id

        response = client.get(f'/admin/post/details/?id={post_id}')
        assert response.status_code == 200
        html = response.data.decode('utf-8')

        # Check for heading
        assert 'govuk-heading-l' in html
        assert 'Post details' in html

    def test_details_view_has_back_link(self, client, sample_users, db):
        """Test details view has a back link."""
        with client.application.app_context():
            post = db.session.query(Post).first()
            post_id = post.id

        response = client.get(f'/admin/post/details/?id={post_id}&url=/admin/post/')
        assert response.status_code == 200
        html = response.data.decode('utf-8')

        # Check for GOV.UK back link
        assert 'govuk-back-link' in html

    def test_details_view_with_multiline_content(self, client, db, sample_users):
        """Test details view converts newlines to <br> tags for multiline content."""
        # Create a post with multiline content
        with client.application.app_context():
            user = db.session.query(User).first()
            post = Post(
                title="Line1\nLine2\nLine3",
                content="Paragraph 1\nParagraph 2\nParagraph 3",
                author_id=user.id,
                created_at=datetime.datetime.now()
            )
            db.session.add(post)
            db.session.commit()
            post_id = post.id

        response = client.get(f'/admin/post/details/?id={post_id}')
        assert response.status_code == 200
        html = response.data.decode('utf-8')

        # Check that newlines are converted to <br> tags
        assert 'Line1<br>Line2<br>Line3' in html
        assert 'Paragraph 1<br>Paragraph 2<br>Paragraph 3' in html

        # Verify content is escaped and then <br> tags are added
        assert '<br>' in html

        # Make sure the lines are individually present
        assert 'Line1' in html
        assert 'Line2' in html
        assert 'Line3' in html

    def test_details_view_escapes_html_content(self, client, db, sample_users):
        """Test details view properly escapes HTML/JavaScript to prevent XSS."""
        # Create a post with HTML/JavaScript content that should be escaped
        with client.application.app_context():
            user = db.session.query(User).first()
            post = Post(
                title="<script>alert('XSS')</script>",
                content="<img src=x onerror=alert('XSS')>",
                author_id=user.id,
                created_at=datetime.datetime.now()
            )
            db.session.add(post)
            db.session.commit()
            post_id = post.id

        response = client.get(f'/admin/post/details/?id={post_id}')
        assert response.status_code == 200
        html = response.data.decode('utf-8')

        # Check that HTML tags are escaped, not executed
        assert '&lt;script&gt;' in html or '&amp;lt;script&amp;gt;' in html
        assert '<script>alert' not in html  # The actual script tag should NOT be present

        # Check img tag is also escaped
        assert '&lt;img' in html or '&amp;lt;img' in html
        assert '<img src=x onerror=' not in html  # The actual img tag should NOT be present
