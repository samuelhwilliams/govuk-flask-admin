import { initAll } from 'govuk-frontend';
import { initAll as initAllMOJ } from '@ministryofjustice/frontend';
import { FilterToggleButton } from '@ministryofjustice/frontend/moj/components/filter-toggle-button/filter-toggle-button.mjs';

initAll();
initAllMOJ();

// Initialize FilterToggleButton separately (not included in initAll)
const filterElements = document.querySelectorAll('[data-module="moj-filter"]');
filterElements.forEach(element => {
  new FilterToggleButton(element);
});
