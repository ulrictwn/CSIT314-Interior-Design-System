'use strict';
const loginRoot = document.querySelector('[data-login-root]');
if (loginRoot) {
  const tabs = [...loginRoot.querySelectorAll('[data-login-audience]')];
  const panels = [...loginRoot.querySelectorAll('[data-login-panel]')];
  const staffRole = loginRoot.querySelector('#staff-role');
  const clearPasswords = () => {
    loginRoot.querySelectorAll('.password-field input').forEach(input => {
      input.value = '';
      input.type = 'password';
    });
    loginRoot.querySelectorAll('[data-password-toggle]').forEach(button => {
      button.setAttribute('aria-pressed', 'false');
      button.setAttribute('aria-label', 'Show password');
    });
  };
  const activate = audience => {
    loginRoot.dataset.audience = audience;
    loginRoot.dataset.role = audience === 'staff' ? staffRole.value : 'customer';
    tabs.forEach(tab => {
      const selected = tab.dataset.loginAudience === audience;
      tab.setAttribute('aria-selected', String(selected));
      tab.tabIndex = selected ? 0 : -1;
    });
    panels.forEach(panel => { panel.hidden = panel.dataset.loginPanel !== audience; });
    clearPasswords();
    loginRoot.querySelectorAll('[data-login-notice]').forEach(notice => { notice.hidden = true; });
    document.title = `${audience === 'staff' ? 'Staff' : 'Customer'} Sign In · Nestora`;
    const address = audience === 'staff' ? staffRole.selectedOptions[0].dataset.loginUrl : tabs[1].href;
    window.history.replaceState({}, '', address);
  };
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', event => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      activate(tab.dataset.loginAudience);
    });
    tab.addEventListener('keydown', event => {
      let next;
      if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') next = tabs[(index + 1) % tabs.length];
      if (event.key === 'Home') next = tabs[0];
      if (event.key === 'End') next = tabs[tabs.length - 1];
      if (next) {
        event.preventDefault();
        activate(next.dataset.loginAudience);
        next.focus();
      }
    });
  });
  staffRole.addEventListener('change', () => {
    clearPasswords();
    loginRoot.dataset.role = staffRole.value;
    window.history.replaceState({}, '', staffRole.selectedOptions[0].dataset.loginUrl);
  });
  loginRoot.querySelectorAll('[data-password-toggle]').forEach(button => {
    button.addEventListener('click', () => {
      const input = document.getElementById(button.dataset.passwordToggle);
      const show = input.type === 'password';
      input.type = show ? 'text' : 'password';
      button.setAttribute('aria-pressed', String(show));
      button.setAttribute('aria-label', show ? 'Hide password' : 'Show password');
    });
  });
}
