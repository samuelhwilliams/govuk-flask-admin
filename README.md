## Developing this extension

### Rebuilding GOV.UK Frontend assets

GOV.UK Flask Admin uses and extends the GOV.UK Frontend CSS and JS in order to add functionality required to display information and action dense admin pages.

These assets are compiled using Flask-Vite.

#### One-off setup

1. Install Node LTS (currently v20)
2. Run `flask vite install`
3. Run `flask vite build` to compile GOV.UK Frontend assets and copy them into `govuk_flask_admin/static`
4. Commit the newly compiled assets.
