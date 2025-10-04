# Filtering Implementation in GOV.UK Flask Admin

This document describes the server-side filtering implementation for govuk-flask-admin that respects GOV.UK Design System principles and accessibility requirements.

## Overview

The filtering system is designed to:
- ✅ Work **without JavaScript** (progressive enhancement)
- ✅ Be fully **keyboard accessible**
- ✅ Support **screen readers** with proper ARIA labels
- ✅ Use native **GOV.UK Design System components**
- ✅ Preserve **all query state** (sorting, search, pagination)
- ✅ Integrate seamlessly with Flask-Admin's existing filter infrastructure

## How It Works

### Server-Side First Approach

All filters are implemented as standard HTML forms that submit via GET requests. JavaScript is only used for optional enhancements like:
- Auto-submitting the page size selector
- Updating bulk action counters
- Client-side validation (not required for core functionality)

### Filter Rendering

Filters are rendered using GOV.UK components based on filter type:

| Filter Type | GOV.UK Component | Example |
|-------------|------------------|---------|
| Text/String | `govukInput` | Email contains "example" |
| Number/Integer | `govukInput` with `inputmode="numeric"` | Age greater than 25 |
| Date | `govukDateInput` | Created after 01/01/2024 |
| Choices/Select | `govukSelect` | Status equals "Active" |
| Boolean | `govukRadios` | Is verified: Yes/No |

### Progressive Disclosure

Filters are placed inside a `govukDetails` component that:
- Shows "Add filters to narrow results" when no filters are active
- Shows "N filter(s) active" when filters are applied
- Automatically expands when filters are active
- Collapses to save screen space when not in use

## Usage

### Basic Configuration

```python
from govuk_flask_admin import GovukModelView

class UserModelView(GovukModelView):
    # Enable filtering on columns
    column_filters = ["age", "email", "created_at", "status"]

    # Enable search
    column_searchable_list = ["email", "name"]

    # Enable page size selection
    can_set_page_size = True
    page_size_options = [10, 25, 50, 100]

    # Enable export
    can_export = True
    export_types = ["csv", "xlsx"]

    # Add descriptions for accessibility
    column_descriptions = {
        "age": "User's age in years",
        "email": "Email address for contacting the user"
    }
```

### Advanced Filter Configuration

You can use Flask-Admin's built-in filter classes for more control:

```python
from flask_admin.contrib.sqla.filters import (
    FilterEqual,
    FilterLike,
    FilterGreater,
    BooleanEqualFilter
)

class UserModelView(GovukModelView):
    column_filters = [
        FilterEqual(column=User.status, name="Status"),
        FilterLike(column=User.email, name="Email"),
        FilterGreater(column=User.age, name="Age"),
        BooleanEqualFilter(column=User.is_active, name="Active")
    ]
```

## Features Implemented

### ✅ Filters
- [x] Text filters (contains, equals, not equals)
- [x] Numeric filters (equals, greater than, less than)
- [x] Date filters (equals, before, after, between)
- [x] Select/Choice filters
- [x] Boolean filters
- [x] Multiple simultaneous filters
- [x] Filter removal (individual tags)
- [x] Clear all filters

### ✅ Search
- [x] Full-text search across searchable columns
- [x] Search preservation with filters
- [x] Clear search button

### ✅ Sorting
- [x] Column header sorting
- [x] Ascending/descending indicators
- [x] Sort state preserved with filters
- [x] Accessible labels (e.g., "Sort by Name, currently sorted ascending")

### ✅ Pagination
- [x] GOV.UK Pagination component
- [x] Page size selector
- [x] State preservation across pages

### ✅ Export
- [x] CSV export
- [x] Export respects current filters and search
- [x] Multiple export format support

### ✅ Bulk Actions
- [x] Checkbox selection
- [x] Select all functionality
- [x] Action dropdown
- [x] Selected item counter
- [x] Keyboard accessible

## Accessibility Features

### Keyboard Navigation
- All controls are keyboard accessible via Tab/Shift+Tab
- Filter form can be submitted with Enter key
- Links and buttons have visible focus indicators

### Screen Reader Support
- Proper label associations for all form fields
- ARIA labels for sort links (e.g., "Sort by Name, currently sorted ascending")
- Hidden labels for checkbox selections
- Clear indication of active filters
- Form validation error announcements

### Progressive Enhancement
- **Level 0 (No CSS/JS)**: All functionality works with plain HTML
- **Level 1 (CSS only)**: Styled with GOV.UK Design System
- **Level 2 (CSS + JS)**: Enhanced interactions (auto-submit, counters)

### WCAG Compliance
- Meets WCAG 2.1 Level AA standards
- Color contrast ratios compliant
- Focus indicators visible
- No JavaScript-only functionality for core features

## Template Structure

```
src/govuk_flask_admin/templates/admin/model/
├── layout.html          # Filter macros and components
├── list.html            # List view with integrated filters
├── create.html          # Create form
├── edit.html            # Edit form
└── details.html         # Detail view
```

### Key Macros in layout.html

- `filter_form()` - Main filter form with all active filters
- `search_form()` - Search input with state preservation
- `page_size_form()` - Page size selector
- `export_options()` - Export links
- `render_filter_input()` - Individual filter field renderer
- `render_filter_group_content()` - Filter group renderer

## State Preservation

The implementation preserves **all query state** across interactions:

When filtering:
- ✅ Current sort column and direction
- ✅ Active search query
- ✅ Page size selection
- ✅ Other active filters
- ✅ Extra query arguments

When searching:
- ✅ Active filters
- ✅ Sort state
- ✅ Page size

When sorting:
- ✅ Active filters
- ✅ Search query
- ✅ Page size

This ensures users never lose their context when interacting with the interface.

## GOV.UK Design Patterns Used

1. **Accordion** - For multiple filter groups (when 3+ groups)
2. **Details** - For collapsible filter section
3. **Date Input** - For date filters (day/month/year)
4. **Select** - For choice-based filters
5. **Input** - For text and numeric filters
6. **Button** - For form submission
7. **Tag** - For active filter indicators
8. **Pagination** - For page navigation
9. **Checkboxes (small)** - For bulk selection

## Examples

### Filter by Age Range
```
User enters: Age greater than 25
URL: /admin/user/?flt0_age=25
```

### Filter by Date
```
User selects: Created after 2024-01-01
URL: /admin/user/?flt0_created_at-day=1&flt0_created_at-month=1&flt0_created_at-year=2024
```

### Multiple Filters + Search + Sort
```
Age > 25 AND Email contains "example" AND sorted by name ascending
URL: /admin/user/?flt0_age=25&flt1_email=example&sort=1&search=john
```

## Browser Support

- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ iOS Safari
- ✅ Chrome Android
- ✅ Works without JavaScript
- ✅ Works without CSS (degraded but functional)

## Performance Considerations

- Server-side filtering means no client-side performance bottlenecks
- All filtering happens in SQLAlchemy queries
- No large dataset transfers to the client
- Suitable for tables with 100,000+ records

## Future Enhancements

Potential improvements for future versions:

- [ ] Date range picker with JavaScript enhancement
- [ ] Autocomplete for text filters with many options
- [ ] Save filter presets
- [ ] Filter history/recent filters
- [ ] URL shortening for complex filter combinations
- [ ] Filter validation hints (e.g., "No results found with these filters")

## Testing

To test the filtering implementation:

1. **Without JavaScript**: Disable JavaScript in your browser and verify all filters work
2. **Keyboard Only**: Navigate using only Tab, Enter, and arrow keys
3. **Screen Reader**: Use NVDA/JAWS on Windows or VoiceOver on macOS
4. **Mobile**: Test on actual mobile devices, not just browser emulators
5. **State Preservation**: Apply filters, then sort/search/paginate and verify filters remain

## Questions?

See the main README or open an issue on GitHub.
