'use strict';
document.documentElement.classList.add('js');

document.querySelectorAll('.permissions-dropdown').forEach(dropdown => {
  const summary = dropdown.querySelector('[data-permission-summary]');
  const update = () => {
    const count = dropdown.querySelectorAll('input[type="checkbox"]:checked').length;
    if (summary) summary.textContent = count ? `${count} permission${count === 1 ? '' : 's'} selected` : 'Select permissions';
  };
  dropdown.addEventListener('change', update);
  update();
});

const menuButton = document.querySelector('.nav-toggle');
if (menuButton) menuButton.addEventListener('click', () => {
  const open = menuButton.closest('.sidebar').classList.toggle('nav-open');
  menuButton.setAttribute('aria-expanded', String(open));
});

