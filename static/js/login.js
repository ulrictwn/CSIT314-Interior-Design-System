'use strict';

const loginRoot = document.querySelector('[data-login-root]');
if (loginRoot) {
  const tabs = [...loginRoot.querySelectorAll('[data-login-role]')];
  const panels = [...loginRoot.querySelectorAll('[data-login-panel]')];
  const activate = (role, updateAddress = true) => {
    loginRoot.dataset.role = role;
    tabs.forEach(tab => {
      const selected = tab.dataset.loginRole === role;
      tab.setAttribute('aria-selected', String(selected));
      tab.tabIndex = selected ? 0 : -1;
    });
    panels.forEach(panel => {
      panel.hidden = panel.dataset.loginPanel !== role;
      panel.querySelectorAll('input[name="password"]').forEach(input => {
        input.value = '';
        input.type = 'password';
      });
    });
    loginRoot.querySelectorAll('[data-password-toggle]').forEach(button => {
      button.setAttribute('aria-pressed', 'false');
      button.setAttribute('aria-label', 'Show password');
    });
    loginRoot.querySelectorAll('[data-login-notice]').forEach(notice => { notice.hidden = true; });
    document.title = `${role === 'admin' ? 'User Admin' : 'Interior Designer'} Sign In · Nestora`;
    const selected = tabs.find(tab => tab.dataset.loginRole === role);
    if (updateAddress && selected) window.history.replaceState({}, '', selected.href);
  };
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', event => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      activate(tab.dataset.loginRole);
    });
    tab.addEventListener('keydown', event => {
      let next;
      if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') next = tabs[(index + 1) % tabs.length];
      if (event.key === 'Home') next = tabs[0];
      if (event.key === 'End') next = tabs[tabs.length - 1];
      if (next) {
        event.preventDefault();
        activate(next.dataset.loginRole);
        next.focus();
      }
    });
  });
  loginRoot.querySelectorAll('[data-password-toggle]').forEach(button => {
    button.addEventListener('click', () => {
      const input = document.getElementById(button.dataset.passwordToggle);
      if (!input) return;
      const show = input.type === 'password';
      input.type = show ? 'text' : 'password';
      button.setAttribute('aria-pressed', String(show));
      button.setAttribute('aria-label', show ? 'Hide password' : 'Show password');
    });
  });
}
