"""E2E tests for GovSelectWithSearch JavaScript enhancement."""
import pytest


@pytest.mark.e2e
class TestSelectWithSearchEnhancement:
    """Test JavaScript enhancement of select-with-search component."""

    def test_select_with_search_enhances_multi_select(self, page):
        """Test that Choices.js enhances multi-select fields with data."""
        # First, go to an edit page to ensure we have data
        # Navigate to user list and click first edit link
        page.goto(f"{page.base_url}/admin/user/")
        page.wait_for_selector('.govuk-table')

        # Click first edit link
        edit_link = page.locator('a:has-text("Edit")').first
        edit_link.click()
        page.wait_for_load_state('networkidle')

        # Wait for Choices.js to initialize on the posts field
        # The posts field is a multi-select with select-with-search
        page.wait_for_selector('.choices', timeout=5000)

        # Check that the select element has the data-module attribute
        select = page.locator('select[name="posts"]')
        assert select.count() > 0, "Select element should exist"
        assert select.get_attribute("data-module") == "select-with-search"
        assert select.get_attribute("multiple") is not None

        # Check that Choices.js has enhanced the select
        choices_wrapper = page.locator('.choices')
        assert choices_wrapper.count() > 0, "Choices.js should enhance the select with .choices wrapper"

        # Check that the wrapper has the GOV.UK gem class
        gem_wrapper = page.locator('.gem-c-select-with-search')
        assert gem_wrapper.count() > 0, "Should have gem-c-select-with-search wrapper"

        # Check that the user's existing posts are shown as selected tags
        selected_items = page.locator('.choices__list--multiple .choices__item')
        selected_count = selected_items.count()

        # Users should have 2-5 posts according to seed_database
        assert selected_count >= 2, f"User should have at least 2 posts selected, found {selected_count}"
        assert selected_count <= 5, f"User should have at most 5 posts selected, found {selected_count}"

    def test_select_with_search_shows_options_on_click(self, page):
        """Test that clicking the select shows a dropdown with options."""
        # Navigate to user edit page which has posts to select
        page.goto(f"{page.base_url}/admin/user/")
        page.wait_for_selector('.govuk-table')

        edit_link = page.locator('a:has-text("Edit")').first
        edit_link.click()
        page.wait_for_load_state('networkidle')

        # Wait for Choices.js to initialize
        page.wait_for_selector('.choices', timeout=5000)

        # Click on the Choices wrapper to open the dropdown
        choices_wrapper = page.locator('.gem-c-select-with-search .choices')
        choices_wrapper.click()

        # Wait for dropdown to appear
        page.wait_for_selector('.choices__list--dropdown', state='visible', timeout=3000)

        # Check that dropdown has options (posts)
        dropdown_items = page.locator('.choices__list--dropdown .choices__item')
        assert dropdown_items.count() > 0, "Dropdown should contain post options"

    def test_select_with_search_search_filters_options(self, page):
        """Test that typing in the search filters the available options."""
        # Navigate to user edit page
        page.goto(f"{page.base_url}/admin/user/")
        page.wait_for_selector('.govuk-table')

        edit_link = page.locator('a:has-text("Edit")').first
        edit_link.click()
        page.wait_for_load_state('networkidle')

        # Wait for Choices.js to initialize
        page.wait_for_selector('.choices', timeout=5000)

        # Click to open dropdown
        choices_wrapper = page.locator('.gem-c-select-with-search .choices')
        choices_wrapper.click()
        page.wait_for_selector('.choices__list--dropdown', state='visible', timeout=3000)

        # Count initial options
        initial_count = page.locator('.choices__list--dropdown .choices__item').count()

        # Type in search box to filter
        search_input = page.locator('.gem-c-select-with-search .choices input[type="search"]')
        search_input.fill("xyz_nonexistent_search_term")

        # Wait a moment for filtering
        page.wait_for_timeout(500)

        # Check that "No results found" message appears or options are filtered
        no_results = page.locator('.choices__item--choice:has-text("No results found")')
        filtered_items = page.locator('.choices__list--dropdown .choices__item--choice')

        # Either we should see "no results" or fewer items than before
        assert no_results.count() > 0 or filtered_items.count() < initial_count, \
            "Search should filter options or show no results message"

    def test_select_with_search_shows_selected_items(self, page):
        """Test that selected items appear as tags."""
        # Navigate to user edit page
        page.goto(f"{page.base_url}/admin/user/")
        page.wait_for_selector('.govuk-table')

        edit_link = page.locator('a:has-text("Edit")').first
        edit_link.click()
        page.wait_for_load_state('networkidle')

        # Wait for Choices.js
        page.wait_for_selector('.choices', timeout=5000)

        # Get initial count of selected items
        initial_selected = page.locator('.choices__list--multiple .choices__item').count()

        # Click to open dropdown
        choices_wrapper = page.locator('.gem-c-select-with-search .choices')
        choices_wrapper.click()
        page.wait_for_selector('.choices__list--dropdown', state='visible', timeout=3000)

        # Select first available option
        first_option = page.locator('.choices__list--dropdown .choices__item--selectable').first
        if first_option.count() > 0:
            option_text = first_option.inner_text()
            first_option.click()

            # Wait for selection to process
            page.wait_for_timeout(500)

            # Check that a new selected item appears
            selected_items = page.locator('.choices__list--multiple .choices__item')
            new_count = selected_items.count()
            assert new_count == initial_selected + 1, \
                f"Should have {initial_selected + 1} selected items, found {new_count}"

            # Verify the newly selected text appears somewhere in the selected items
            all_selected_text = " ".join([selected_items.nth(i).inner_text() for i in range(new_count)])
            assert option_text in all_selected_text, \
                f"Selected item '{option_text}' should appear in selected tags"

    def test_select_with_search_remove_selected_item(self, page):
        """Test that clicking the X removes a selected item."""
        # Navigate to user edit page
        page.goto(f"{page.base_url}/admin/user/")
        page.wait_for_selector('.govuk-table')

        edit_link = page.locator('a:has-text("Edit")').first
        edit_link.click()
        page.wait_for_load_state('networkidle')

        # Wait for Choices.js
        page.wait_for_selector('.choices', timeout=5000)

        # Select an item first
        choices_wrapper = page.locator('.gem-c-select-with-search .choices')
        choices_wrapper.click()
        page.wait_for_selector('.choices__list--dropdown', state='visible', timeout=3000)

        first_option = page.locator('.choices__list--dropdown .choices__item--selectable').first
        if first_option.count() > 0:
            first_option.click()
            page.wait_for_timeout(500)

            # Now try to remove it
            selected_items = page.locator('.choices__list--multiple .choices__item')
            initial_count = selected_items.count()

            # Click the remove button (X)
            remove_button = selected_items.first.locator('.choices__button')
            if remove_button.count() > 0:
                remove_button.click()
                page.wait_for_timeout(500)

                # Check that item was removed
                final_count = page.locator('.choices__list--multiple .choices__item').count()
                assert final_count < initial_count, "Clicking X should remove the selected item"

    def test_select_with_search_has_label(self, page):
        """Test that the label is visible above the select field."""
        page.goto(f"{page.base_url}/admin/user/new/")

        # Check that the posts field has a visible label
        posts_label = page.locator('label[for="posts"]')
        assert posts_label.is_visible()
        assert "Posts" in posts_label.inner_text()

    def test_select_with_search_fallback_without_js(self, page):
        """Test that the select works as a native multi-select without JavaScript."""
        # Disable JavaScript by blocking JS files
        page.route("**/*.js", lambda route: route.abort())

        page.goto(f"{page.base_url}/admin/user/new/")

        # The select should still be present and functional
        select = page.locator('select[name="posts"]')
        assert select.is_visible()
        assert select.get_attribute("multiple") is not None

        # No Choices.js wrapper should exist
        choices_wrapper = page.locator('.choices')
        assert choices_wrapper.count() == 0, "No Choices.js enhancement without JavaScript"

    def test_select_with_search_accessible_attributes(self, page):
        """Test that accessible attributes are preserved after JavaScript enhancement."""
        page.goto(f"{page.base_url}/admin/user/new/")

        # Wait for Choices.js to enhance the select
        page.wait_for_selector('.choices', timeout=5000)

        # Check that the original select element still has proper attributes
        # (Choices.js hides it but should preserve attributes)
        select = page.locator('select[name="posts"]')
        assert select.count() > 0, "Select element should exist"
        assert select.get_attribute("id") == "posts"
        assert select.get_attribute("name") == "posts"

        # Check that label is associated with the field
        posts_label = page.locator('label[for="posts"]')
        assert posts_label.count() > 0

    def test_user_edit_shows_all_posts_in_dropdown(self, page):
        """Test that editing a user shows ALL posts (from all users) in the dropdown."""
        # Navigate to user edit page
        page.goto(f"{page.base_url}/admin/user/")
        page.wait_for_selector('.govuk-table')

        edit_link = page.locator('a:has-text("Edit")').first
        edit_link.click()
        page.wait_for_load_state('networkidle')

        # Wait for Choices.js
        page.wait_for_selector('.choices', timeout=5000)

        # Click to open dropdown
        choices_wrapper = page.locator('.gem-c-select-with-search .choices')
        choices_wrapper.click()
        page.wait_for_selector('.choices__list--dropdown', state='visible', timeout=3000)

        # Count all available options in dropdown
        dropdown_items = page.locator('.choices__list--dropdown .choices__item--choice')
        dropdown_count = dropdown_items.count()

        # Should have approximately 20 posts total (each user has 2-5 posts, 8 users)
        # Minus the ones already selected for this user
        assert dropdown_count >= 10, f"Should have at least 10 posts in dropdown, found {dropdown_count}"

    def test_user_edit_can_add_post_and_persist(self, page):
        """Test that adding a post to a user persists after save and reload."""
        # Navigate to user edit page
        page.goto(f"{page.base_url}/admin/user/")
        page.wait_for_selector('.govuk-table')

        edit_link = page.locator('a:has-text("Edit")').first
        edit_link.click()
        page.wait_for_load_state('networkidle')

        # Wait for Choices.js
        page.wait_for_selector('.choices', timeout=5000)

        # Count initial selected posts
        initial_selected = page.locator('.choices__list--multiple .choices__item').count()

        # Click to open dropdown
        choices_wrapper = page.locator('.gem-c-select-with-search .choices')
        choices_wrapper.click()
        page.wait_for_selector('.choices__list--dropdown', state='visible', timeout=3000)

        # Select first available (unselected) option
        available_options = page.locator('.choices__list--dropdown .choices__item--selectable')
        assert available_options.count() > 0, "Should have at least one post available to add"

        added_post_title = available_options.first.inner_text()
        available_options.first.click()
        page.wait_for_timeout(500)

        # Verify the new selection appears as a tag
        new_selected_count = page.locator('.choices__list--multiple .choices__item').count()
        assert new_selected_count == initial_selected + 1, \
            f"Should have {initial_selected + 1} posts selected, found {new_selected_count}"

        # Save the form
        save_button = page.locator('input[type="submit"][value="Save"]')
        save_button.click()
        page.wait_for_load_state('networkidle')

        # Verify success
        assert "/admin/user/" in page.url
        success_message = page.locator('.govuk-notification-banner--success')
        assert success_message.count() > 0, "Should show success message after saving"

        # Go back to edit the same user to verify persistence
        edit_link = page.locator('a:has-text("Edit")').first
        edit_link.click()
        page.wait_for_load_state('networkidle')
        page.wait_for_selector('.choices', timeout=5000)

        # Verify the added post is still selected
        final_selected = page.locator('.choices__list--multiple .choices__item')
        final_count = final_selected.count()
        assert final_count == initial_selected + 1, \
            f"After reload, should still have {initial_selected + 1} posts, found {final_count}"

        # Verify the added post title appears in the selected items
        all_selected_text = " ".join([final_selected.nth(i).inner_text() for i in range(final_count)])
        assert added_post_title in all_selected_text, \
            f"Added post '{added_post_title}' should still be selected after reload"

    def test_user_edit_can_remove_post_and_persist(self, page):
        """Test that removing a post from a user persists after save and reload."""
        # Navigate to user edit page
        page.goto(f"{page.base_url}/admin/user/")
        page.wait_for_selector('.govuk-table')

        edit_link = page.locator('a:has-text("Edit")').first
        edit_link.click()
        page.wait_for_load_state('networkidle')

        # Wait for Choices.js
        page.wait_for_selector('.choices', timeout=5000)

        # Get initial selected posts
        selected_items = page.locator('.choices__list--multiple .choices__item')
        initial_count = selected_items.count()
        assert initial_count > 0, "User should have at least one post to remove"

        # Get the title of the first post (remove "Remove item" button text)
        first_item_text = selected_items.first.inner_text()
        removed_post_title = first_item_text.replace("Remove item", "").strip()

        # Click remove button on first post
        remove_button = selected_items.first.locator('.choices__button')
        remove_button.click()
        page.wait_for_timeout(500)

        # Verify post was removed from selected items
        new_count = page.locator('.choices__list--multiple .choices__item').count()
        assert new_count == initial_count - 1, \
            f"Should have {initial_count - 1} posts after removal, found {new_count}"

        # Save the form
        save_button = page.locator('input[type="submit"][value="Save"]')
        save_button.click()
        page.wait_for_load_state('networkidle')

        # Verify success
        assert "/admin/user/" in page.url
        success_message = page.locator('.govuk-notification-banner--success')
        assert success_message.count() > 0, "Should show success message after saving"

        # Go back to edit the same user to verify persistence
        edit_link = page.locator('a:has-text("Edit")').first
        edit_link.click()
        page.wait_for_load_state('networkidle')
        page.wait_for_selector('.choices', timeout=5000)

        # Verify the post count is still reduced
        final_selected = page.locator('.choices__list--multiple .choices__item')
        final_count = final_selected.count()
        assert final_count == initial_count - 1, \
            f"After reload, should still have {initial_count - 1} posts, found {final_count}"

        # Verify the removed post is NO LONGER in the selected items
        all_selected_text = " ".join([final_selected.nth(i).inner_text() for i in range(final_count)])
        assert removed_post_title not in all_selected_text, \
            f"Removed post '{removed_post_title}' should not be selected after reload"
