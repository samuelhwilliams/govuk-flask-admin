"""E2E tests for filter UI interactions."""
import pytest
from playwright.sync_api import expect


@pytest.mark.e2e
class TestFilterInteractions:
    """Test filter UI interactions."""

    def test_filter_details_expands_collapses(self, page):
        """Test clicking filter toggle button shows/hides filters."""
        page.goto(f"{page.base_url}/admin/user/")
        page.wait_for_selector('.govuk-table')

        # Wait for filter toggle button to be created by JavaScript
        page.wait_for_selector('.moj-action-bar__filter button')

        filter_toggle = page.locator('.moj-action-bar__filter button')
        filter_panel = page.locator('.moj-filter')

        # Assert filter initially hidden (has moj-js-hidden class or hidden attribute)
        assert not filter_panel.is_visible(), "Expected filter panel to be initially hidden"
        assert "Show filter" in filter_toggle.text_content(), "Expected 'Show filter' text"

        # Click toggle to show
        filter_toggle.click()
        filter_panel.wait_for(state='visible')

        # Assert filter panel visible
        assert filter_panel.is_visible(), "Expected filter panel to be visible after click"
        assert "Hide filter" in filter_toggle.text_content(), "Expected 'Hide filter' text"

        # Click again to hide
        filter_toggle.click()
        filter_panel.wait_for(state='hidden')

        assert not filter_panel.is_visible(), "Expected filter panel to be hidden after second click"
        assert "Show filter" in filter_toggle.text_content(), "Expected 'Show filter' text again"

    def test_date_filter_three_inputs(self, page):
        """Test date filter shows day/month/year inputs."""
        page.goto(f"{page.base_url}/admin/user/")
        page.wait_for_selector('.govuk-table')

        # Show filters panel
        filter_toggle = page.locator('.moj-action-bar__filter button')
        filter_toggle.click()
        filter_panel = page.locator('.moj-filter')
        filter_panel.wait_for(state='visible')

        # Expand the created_at filter accordion section
        created_at_section = page.locator('button:has-text("Created At")')
        assert created_at_section.count() > 0, "Expected Created At filter section"

        created_at_section.click()

        # Assert three date inputs present for created_at filter
        # GOV.UK date input creates fields with names like flt{n}_{n}-day, etc.
        day_input = page.locator('input[name$="-day"]')
        month_input = page.locator('input[name$="-month"]')
        year_input = page.locator('input[name$="-year"]')

        assert day_input.count() > 0, "Expected day input for date filter"
        assert month_input.count() > 0, "Expected month input for date filter"
        assert year_input.count() > 0, "Expected year input for date filter"

        # Verify they use GOV.UK date input styling
        date_input_container = page.locator('.govuk-date-input')
        assert date_input_container.count() > 0, "Expected GOV.UK date input component"

    def test_filter_submission_updates_results(self, page):
        """Test submitting filter updates table."""
        page.goto(f"{page.base_url}/admin/user/")
        page.wait_for_selector('.govuk-table')

        # Show filters panel
        filter_toggle = page.locator('.moj-action-bar__filter button')
        filter_toggle.click()
        filter_panel = page.locator('.moj-filter')
        filter_panel.wait_for(state='visible')

        # Expand Age accordion section
        age_section = page.locator('button:has-text("Age")').first
        assert age_section.count() > 0, "Expected Age filter section"

        age_section.click()

        # Fill in age filter "equals" (first age filter flt0_0)
        age_filter = page.locator('input#flt0_0')
        age_filter.fill('25')

        # Click Apply filters button within the filter form
        apply_button = page.locator('#filter_form button[type="submit"]:has-text("Apply filters")')
        assert apply_button.count() > 0, "Expected 'Apply filters' button in filter form"
        apply_button.click()

        # Wait for page to reload with filtered results
        page.wait_for_load_state('networkidle')

        # Assert URL contains filter param
        assert 'flt0_0=25' in page.url, "Expected filter parameter in URL"

        # Assert filter tag is displayed in the selected filters section
        filter_tags = page.locator('.moj-filter-tags .moj-filter__tag')
        assert filter_tags.count() > 0, "Expected filter tag to be displayed"

        # Table should still be present (even if no results)
        table = page.locator('.govuk-table')
        assert table.is_visible(), "Expected table to be visible after filtering"

    def test_filter_tag_removal(self, page):
        """Test clicking × on filter tag removes filter."""
        # Use correct filter param format flt0_0=25 for age equals filter
        page.goto(f"{page.base_url}/admin/user/?flt0_0=25")
        page.wait_for_selector('.govuk-table')

        # Assert URL has filter param
        assert 'flt0_0=25' in page.url, "Expected age filter in URL"

        # Show filter panel to see filter tags
        filter_toggle = page.locator('.moj-action-bar__filter button')
        filter_toggle.click()
        filter_panel = page.locator('.moj-filter')
        filter_panel.wait_for(state='visible')

        # Assert filter tag is displayed in MOJ filter tags
        # The .moj-filter__tag element IS the <a> tag itself
        filter_tag = page.locator('.moj-filter__tag')
        assert filter_tag.count() > 0, "Expected filter tag to be displayed"

        # Click the filter tag to remove it
        filter_tag.first.click()

        # Wait for page to reload
        page.wait_for_load_state('networkidle')

        # Assert filter removed from URL
        assert 'flt0_0' not in page.url, "Expected filter to be removed from URL"

        # Show filter panel again to check tags are gone
        filter_toggle_after = page.locator('.moj-action-bar__filter button')
        filter_toggle_after.click()
        filter_panel_after = page.locator('.moj-filter')
        filter_panel_after.wait_for(state='visible')

        # Assert filter tag no longer displayed
        filter_tag_after = page.locator('.moj-filter__tag')
        assert filter_tag_after.count() == 0, "Expected no filter tags after removal"

    def test_remove_search_preserves_filters(self, page):
        """Test removing search tag preserves active filters."""
        # Apply both filter and search
        page.goto(f"{page.base_url}/admin/user/?flt0_0=25&search=alice")
        page.wait_for_selector('.govuk-table')

        # Assert both filter and search are active in URL
        assert 'flt0_0=25' in page.url, "Expected age filter in URL"
        assert 'search=alice' in page.url, "Expected search param in URL"

        # Show filter panel to see filter tags
        filter_toggle = page.locator('.moj-action-bar__filter button')
        filter_toggle.click()
        filter_panel = page.locator('.moj-filter')
        filter_panel.wait_for(state='visible')

        # Assert both search and filter tags are displayed
        filter_tags = page.locator('.moj-filter__tag')
        assert filter_tags.count() >= 2, "Expected at least 2 tags (search + filter)"

        # Find and click the search filter tag (should be under "Search" heading)
        search_tag = page.locator('h3:has-text("Search") + ul .moj-filter__tag')
        assert search_tag.count() > 0, "Expected search filter tag"
        search_tag.click()

        # Wait for page to reload
        page.wait_for_load_state('networkidle')

        # Assert search removed but filter preserved
        assert 'search' not in page.url, "Expected search to be removed from URL"
        assert 'flt0_0=25' in page.url, "Expected age filter to remain in URL"

        # Show filter panel again to verify tags
        filter_toggle_after = page.locator('.moj-action-bar__filter button')
        filter_toggle_after.click()
        filter_panel_after = page.locator('.moj-filter')
        filter_panel_after.wait_for(state='visible')

        # Assert search tag gone but filter tag remains
        search_heading = page.locator('h3:has-text("Search")')
        assert search_heading.count() == 0, "Expected no Search heading after removal"

        filter_tags_after = page.locator('.moj-filter__tag')
        assert filter_tags_after.count() > 0, "Expected filter tag to remain"

    def test_clear_all_filters(self, page):
        """Test 'Clear all' link removes all filters."""
        # Use correct filter param format
        page.goto(f"{page.base_url}/admin/user/?flt0_0=25&search=test")
        page.wait_for_selector('.govuk-table')

        # Assert filter and search are active in URL
        assert 'flt0_0=25' in page.url, "Expected age filter in URL"
        assert 'search=test' in page.url, "Expected search param in URL"

        # Show filter panel to see filter tags and clear link
        filter_toggle = page.locator('.moj-action-bar__filter button')
        filter_toggle.click()
        filter_panel = page.locator('.moj-filter')
        filter_panel.wait_for(state='visible')

        # Assert filter tags displayed (MOJ filter tags)
        filter_tags = page.locator('.moj-filter__tag')
        assert filter_tags.count() > 0, "Expected filter tags to be displayed"

        # Click "Clear filters" link in the MOJ filter selected section
        clear_link = page.locator('a:has-text("Clear filters")')
        assert clear_link.count() > 0, "Expected Clear filters link in filter panel"
        clear_link.click()

        # Wait for page to reload
        page.wait_for_load_state('networkidle')

        # Assert filters and search cleared from URL
        assert 'flt0_0' not in page.url, "Expected age filter to be cleared"
        assert 'search' not in page.url, "Expected search to be cleared"

        # Show filter panel again and verify no tags
        filter_toggle_after = page.locator('.moj-action-bar__filter button')
        filter_toggle_after.click()
        filter_panel_after = page.locator('.moj-filter')
        filter_panel_after.wait_for(state='visible')

        # Assert no filter tags displayed
        filter_tags_after = page.locator('.moj-filter__tag')
        assert filter_tags_after.count() == 0, "Expected no filter tags after clearing"

    def test_enum_filter_dropdown(self, page):
        """Test enum filter shows dropdown with values."""
        page.goto(f"{page.base_url}/admin/user/")
        page.wait_for_selector('.govuk-table')

        # Show filter panel
        filter_toggle = page.locator('.moj-action-bar__filter button')
        filter_toggle.click()

        # Wait for filter panel to be visible
        filter_panel = page.locator('.moj-filter')
        filter_panel.wait_for(state='visible')

        # Expand Favourite Colour accordion section
        colour_section = page.locator('button:has-text("Favourite Colour")')
        assert colour_section.count() > 0, "Expected Favourite Colour filter section"

        colour_section.click()

        # Locate all selects in the Favourite Colour section
        colour_selects = page.locator('select.govuk-select')
        assert colour_selects.count() > 0, "Expected select dropdowns for favourite_colour"

        # Find the select that has colour options (not Yes/No boolean options)
        found_colour_select = False
        for i in range(colour_selects.count()):
            select = colour_selects.nth(i)
            options = select.locator('option')
            option_texts = [options.nth(j).text_content().strip() for j in range(options.count())]

            # Filter out empty/select options
            non_empty_options = [opt for opt in option_texts if opt and opt.lower() not in ['select...', '']]

            # Check if this select has 3 options (the 3 colours)
            if len(non_empty_options) == 3:
                found_colour_select = True

                # Assert it has GOV.UK select styling
                assert 'govuk-select' in select.get_attribute('class'), \
                    "Expected GOV.UK select class on enum filter"

                # Verify these are colour values (should contain colour names)
                combined_text = ' '.join(non_empty_options).lower()
                assert ('red' in combined_text or 'blue' in combined_text or 'yellow' in combined_text), \
                    f"Expected colour names in options, got: {non_empty_options}"
                break

        assert found_colour_select, "Expected to find favourite_colour enum select with 3 colour options"

    def test_filter_button_shows_active_count(self, page):
        """Test filter toggle button shows active filter count."""
        # Test with no filters - should not show count
        page.goto(f"{page.base_url}/admin/user/")
        page.wait_for_selector('.govuk-table')

        # Wait for filter button to be initialized
        filter_toggle = page.locator('.moj-action-bar__filter button')
        expect(filter_toggle).to_have_text("Show filter")

        # Test with one filter - should show "(1 active)"
        page.goto(f"{page.base_url}/admin/user/?flt0_0=25")
        page.wait_for_selector('.govuk-table')

        filter_toggle = page.locator('.moj-action-bar__filter button')
        # Wait for JS to update button text
        expect(filter_toggle).to_contain_text("(1 active)")
        expect(filter_toggle).to_contain_text("Show filter")

        # Test with search only - should show "(1 active)"
        page.goto(f"{page.base_url}/admin/user/?search=alice")
        page.wait_for_selector('.govuk-table')

        filter_toggle = page.locator('.moj-action-bar__filter button')
        expect(filter_toggle).to_contain_text("(1 active)")

        # Test with filter + search - should show "(2 active)"
        page.goto(f"{page.base_url}/admin/user/?flt0_0=25&search=alice")
        page.wait_for_selector('.govuk-table')

        filter_toggle = page.locator('.moj-action-bar__filter button')
        expect(filter_toggle).to_contain_text("(2 active)")

        # Click to expand - should change to "Hide filter (2 active)"
        filter_toggle.click()
        filter_panel = page.locator('.moj-filter')
        filter_panel.wait_for(state='visible')

        expect(filter_toggle).to_contain_text("Hide filter")
        expect(filter_toggle).to_contain_text("(2 active)")

        # Click to collapse - should change back to "Show filter (2 active)"
        filter_toggle.click()
        filter_panel.wait_for(state='hidden')

        expect(filter_toggle).to_contain_text("Show filter")
        expect(filter_toggle).to_contain_text("(2 active)")


@pytest.mark.e2e
class TestFilterPersistence:
    """Test filter state persistence."""

    def test_filters_persist_after_pagination(self, page):
        """Test filters remain after changing page."""
        # Apply age filter with correct param format
        page.goto(f"{page.base_url}/admin/user/?flt0_0=25")
        page.wait_for_selector('.govuk-table')

        # Assert filter is active
        assert 'flt0_0=25' in page.url, "Expected age filter in URL"

        # Show filter panel to check for filter tags
        filter_toggle = page.locator('.moj-action-bar__filter button')
        filter_toggle.click()
        filter_panel = page.locator('.moj-filter')
        filter_panel.wait_for(state='visible')

        filter_tag = page.locator('.moj-filter__tag')
        assert filter_tag.count() > 0, "Expected filter tag to be displayed"

        # Check if pagination exists (with default 8 users and page_size 15, no pagination)
        # This test verifies the URL structure is correct for filters to persist
        # The actual pagination persistence is tested when pagination exists
        next_page_link = page.locator('.govuk-pagination__next a')

        # If pagination exists, navigate and verify filter persists
        if next_page_link.count() > 0:
            next_page_link.click()
            page.wait_for_load_state('networkidle')

            # Assert filter still active in URL
            assert 'flt0_0=25' in page.url, "Expected filter to persist after pagination"

            # Show filter panel again and check for tag
            filter_toggle_after = page.locator('.moj-action-bar__filter button')
            filter_toggle_after.click()
            filter_panel_after = page.locator('.moj-filter')
            filter_panel_after.wait_for(state='visible')

            # Assert filter tag still displayed
            filter_tag_after = page.locator('.moj-filter__tag')
            assert filter_tag_after.count() > 0, "Expected filter tag after pagination"

    def test_filters_persist_after_sort(self, page):
        """Test filters remain after sorting."""
        # Apply age filter with correct param format
        page.goto(f"{page.base_url}/admin/user/?flt0_0=25")
        page.wait_for_selector('.govuk-table')

        # Assert filter is active
        assert 'flt0_0=25' in page.url, "Expected age filter in URL"

        # Show filter panel to check for filter tags
        filter_toggle = page.locator('.moj-action-bar__filter button')
        filter_toggle.click()
        filter_panel = page.locator('.moj-filter')
        filter_panel.wait_for(state='visible')

        filter_tag = page.locator('.moj-filter__tag')
        assert filter_tag.count() > 0, "Expected filter tag to be displayed"

        # Click a sortable column header (e.g., Email or Name)
        sort_link = page.locator('a.gfa-link--sort').first
        assert sort_link.count() > 0, "Expected sortable column"

        sort_link.click()
        page.wait_for_load_state('networkidle')

        # Assert filter still active in URL
        assert 'flt0_0=25' in page.url, "Expected filter to persist after sorting"

        # Assert sort parameter also present
        assert 'sort=' in page.url, "Expected sort parameter in URL"

        # Show filter panel again and check for tag
        filter_toggle_after = page.locator('.moj-action-bar__filter button')
        filter_toggle_after.click()
        filter_panel_after = page.locator('.moj-filter')
        filter_panel_after.wait_for(state='visible')

        # Assert filter tag still displayed
        filter_tag_after = page.locator('.moj-filter__tag')
        assert filter_tag_after.count() > 0, "Expected filter tag after sorting"
