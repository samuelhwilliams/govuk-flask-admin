# TODO

## High priority

- Move the navigation bar to the top (service navigation? might require dropdowns which would mean JS which would 
  mean sad)
- Refine layout of all of the views
- The model list table has a scrollbar visible even when it doesn't need one - some layout issue probably from my 
  custom styling, FIX IT.
- Move the show/hide filter + action menu and results # + pagination + # per page outside of the scroll container. 
  If possible?
- fix filter tags - asset loading/content shown
- fix links from list view to model view page with `can_edit=false` (currently goes to edit page which redirects back to list view)

## Other

- Work out how to support different versions of GOV.UK Frontend
- Maybe rethink baking GOV.UK Frontend assets into this extension directly - but what's a better option if we need to extend GOV.UK Frontend with custom functionality+styling?
- think more about i18n/l10n
- think about performance for large/extra large tables
- make default error messages (eg for Unique, InputRequired, IntegerField) more GOVUK-style/accessible.

## UI

- Fileadmin (s3)
