'use strict';
const reportForm = document.querySelector('[data-report-kind]');
if (reportForm) {
  const start = reportForm.querySelector('#startDate');
  const end = reportForm.querySelector('#endDate');
  const iso = date => date.toISOString().slice(0, 10);
  start.addEventListener('change', () => {
    if (!start.value) return;
    const date = new Date(`${start.value}T00:00:00Z`);
    if (Number.isNaN(date.getTime())) return;
    const kind = reportForm.dataset.reportKind;
    if (kind === 'weekly') date.setUTCDate(date.getUTCDate() + 6);
    if (kind === 'monthly') {
      date.setUTCDate(1);
      start.value = iso(date);
      date.setUTCMonth(date.getUTCMonth() + 1);
      date.setUTCDate(0);
    }
    end.value = iso(date);
  });
}
