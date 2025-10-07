import { initAll } from 'govuk-frontend';
import { initAll as initAllMOJ } from '@ministryofjustice/frontend';
import { FilterToggleButton } from '@ministryofjustice/frontend/moj/components/filter-toggle-button/filter-toggle-button.mjs';

initAll();
initAllMOJ();

// Initialize FilterToggleButton separately (not included in initAll)
const filterElements = document.querySelectorAll('[data-module="moj-filter"]');
filterElements.forEach(element => {
  // Prevent scroll when filter panel is focused by overriding the focus method
  const originalFocus = element.focus;
  element.focus = function() {
    originalFocus.call(this, { preventScroll: true });
  };

  new FilterToggleButton(element);
});
