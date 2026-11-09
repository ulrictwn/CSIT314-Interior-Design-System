from boundary.validation import strip_input
from datetime import date
from flask import flash, redirect, url_for
from flask.views import MethodView
from boundary.designer.context import request_values
from boundary.designer.presentation import wants_html
from boundary.portal import optional_account_id, present, error_response
from boundary.reports.presentation import default_dates
from control.reports.daily_report_controller import DailyReportController
from entity.reports.report import Report
from infrastructure.errors import DomainError


class DailyReportPage(MethodView):
    def get(self):
        return present(dict(ok=True, kind='daily', values=default_dates('daily')),
                       'reports/form.html', 'Generate Daily Report', 'manager')

    def post(self):
        values = request_values()
        self.submitted_end_date = values.get('endDate')
        self.onGenerateDailyReport(values.get('startDate', ''))
        return self.rendered_page

    def onGenerateDailyReport(self, startDate: date) -> None:
        self.values = dict(startDate=strip_input(startDate), endDate=strip_input(getattr(self, 'submitted_end_date', None)))
        try:
            controller = DailyReportController(accountId=optional_account_id(), endDate=self.values['endDate'])
            report = controller.generateDailyReport(self.values['startDate'])
        except DomainError as error:
            self.error_message, self.field_errors = str(error), getattr(error, 'field_errors', {})
            self._display_error()
            return
        self.displayReport(report)

    def displayReport(self, report: Report) -> None:
        if wants_html():
            flash('Daily report generated successfully.', 'success')
            self.rendered_page = redirect(url_for('view_report', report_id=report.report_id), code=303)
        else:
            self.rendered_page = dict(ok=True, report=report.as_dict()), 201

    def _display_error(self) -> None:
        self.rendered_page = error_response(self.error_message, 'manager', self.field_errors,
            values=self.values, template='reports/form.html', kind='daily')
