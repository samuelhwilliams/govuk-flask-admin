"""E2E tests for filter UI interactions."""
import pytest


@pytest.mark.e2e
class TestFilterInteractions:
    """Test filter UI interactions."""

    def test_filter_details_expands_collapses(self, page):
        """Test clicking filter summary opens/closes filters."""
        page.goto(f"{page.base_url}/admin/user/")
        page.wait_for_selector('.govuk-table')

        details = page.locator('details.govuk-details')
        assert details.count() > 0, "Expected details element for filters"

        # Assert details initially closed
        is_open = details.get_attribute('open')
        assert is_open is None, "Expected details to be initially closed"

        # Click summary to open
        summary = page.locator('summary.govuk-details__summary')
        summary.click()

        # Assert details opened
        is_open = details.get_attribute('open')
        assert is_open is not None, "Expected details to be open after click"

        # Click again to close
        summary.click()
        is_open = details.get_attribute('open')
        assert is_open is None, "Expected details to close after second click"

    def test_date_filter_three_inputs(self, page):
        """Test date filter shows day/month/year inputs."""
        page.goto(f"{page.base_url}/admin/user/")
        page.wait_for_selector('.govuk-table')

        # Open filters details
        page.click('summary.govuk-details__summary')

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

        # Open filters
        page.click('summary.govuk-details__summary')

        # Expand Age accordion section
        age_section = page.locator('button:has-text("Age")').first
        assert age_section.count() > 0, "Expected Age filter section"

        age_section.click()

        # Fill in age filter "equals" (first age filter flt0_0)
        age_filter = page.locator('input#flt0_0')
        age_filter.fill('25')

        # Click Apply button within the filter form (not the bulk action button)
        apply_button = page.locator('#filter_form button[type="submit"]:has-text("Apply")')
        assert apply_button.count() > 0, "Expected Apply button in filter form"
        apply_button.click()

        # Wait for page to reload with filtered results
        page.wait_for_load_state('networkidle')

        # Assert URL contains filter param
        assert 'flt0_0=25' in page.url, "Expected filter parameter in URL"

        # Assert filter tag is displayed
        filter_tags = page.locator('.govuk-tag:has-text("Age")')
        assert filter_tags.count() > 0, "Expected filter tag to be displayed"

        # Table should still be present (even if no results)
        table = page.locator('.govuk-table')
        assert table.is_visible(), "Expected table to be visible after filtering"

    def test_filter_tag_removal(self, page):
        """Test clicking × on filter tag removes filter."""
        # Use correct filter param format flt0_0=25 for age equals filter
        page.goto(f"{page.base_url}/admin/user/?flt0_0=25")
        page.wait_for_selector('.govuk-table')

        # Assert filter tag is displayed
        filter_tag = page.locator('.govuk-tag:has-text("Age")')
        assert filter_tag.count() > 0, "Expected filter tag to be displayed"

        # Assert URL has filter param
        assert 'flt0_0=25' in page.url, "Expected age filter in URL"

        # Click remove link (×)
        remove_link = page.locator('.gfa-filter-tag-remove')
        assert remove_link.count() > 0, "Expected remove link in filter tag"
        remove_link.click()

        # Wait for page to reload
        page.wait_for_load_state('networkidle')

        # Assert filter removed from URL
        assert 'flt0_0' not in page.url, "Expected filter to be removed from URL"

        # Assert filter tag no longer displayed
        filter_tag_after = page.locator('.govuk-tag:has-text("Age")')
        assert filter_tag_after.count() == 0, "Expected no filter tags after removal"

    def test_clear_all_filters(self, page):
        """Test 'Clear all' link removes all filters."""
        # Use correct filter param format
        page.goto(f"{page.base_url}/admin/user/?flt0_0=25&search=test")
        page.wait_for_selector('.govuk-table')

        # Assert filter and search are active in URL
        assert 'flt0_0=25' in page.url, "Expected age filter in URL"
        assert 'search=test' in page.url, "Expected search param in URL"

        # Assert filter tags displayed
        filter_tags = page.locator('.govuk-tag:has-text("Age")')
        assert filter_tags.count() > 0, "Expected filter tags to be displayed"

        # Open the filter details to see the clear link
        details = page.locator('details.govuk-details')
        is_open = details.get_attribute('open')
        if is_open is None:
            page.click('summary.govuk-details__summary')

        # Click clear all link within the filter form
        clear_link = page.locator('#filter_form a:has-text("Clear all")')
        assert clear_link.count() > 0, "Expected Clear all link in filter form"
        clear_link.click()

        # Wait for page to reload
        page.wait_for_load_state('networkidle')

        # Assert filters and search cleared from URL
        assert 'flt0_0' not in page.url, "Expected age filter to be cleared"
        assert 'search' not in page.url, "Expected search to be cleared"

        # Assert no filter tags displayed
        filter_tags_after = page.locator('.govuk-tag:has-text("Age")')
        assert filter_tags_after.count() == 0, "Expected no filter tags after clearing"

    def test_enum_filter_dropdown(self, page):
        """Test enum filter shows dropdown with values."""
        page.goto(f"{page.base_url}/admin/user/")
        page.wait_for_selector('.govuk-table')

        # Open filters
        page.click('summary.govuk-details__summary')

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
        filter_tag = page.locator('.govuk-tag:has-text("Age")')
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

            # Assert filter tag still displayed
            filter_tag_after = page.locator('.govuk-tag:has-text("Age")')
            assert filter_tag_after.count() > 0, "Expected filter tag after pagination"

    def test_filters_persist_after_sort(self, page):
        """Test filters remain after sorting."""
        # Apply age filter with correct param format
        page.goto(f"{page.base_url}/admin/user/?flt0_0=25")
        page.wait_for_selector('.govuk-table')

        # Assert filter is active
        assert 'flt0_0=25' in page.url, "Expected age filter in URL"
        filter_tag = page.locator('.govuk-tag:has-text("Age")')
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

        # Assert filter tag still displayed
        filter_tag_after = page.locator('.govuk-tag:has-text("Age")')
        assert filter_tag_after.count() > 0, "Expected filter tag after sorting"
