from boundary.validation import strip_input
from datetime import date
from flask import flash, redirect, url_for
from flask.views import MethodView
from boundary.designer.context import request_values
from boundary.designer.presentation import wants_html
from boundary.portal import optional_account_id, present, error_response
from boundary.reports.presentation import default_dates
from control.reports.monthly_report_controller import MonthlyReportController
from entity.reports.report import Report
from infrastructure.errors import DomainError


class MonthlyReportPage(MethodView):
    def get(self):
        return present(dict(ok=True, kind='monthly', values=default_dates('monthly')),
                       'reports/form.html', 'Generate Monthly Report', 'manager')

    def post(self):
        values = request_values()
        self.onGenerateMonthlyReport(values.get('startDate', ''), values.get('endDate', ''))
        return self.rendered_page

    def onGenerateMonthlyReport(self, startDate: date, endDate: date) -> None:
        self.values = dict(startDate=strip_input(startDate), endDate=strip_input(endDate))
        try:
            controller = MonthlyReportController(accountId=optional_account_id())
            report = controller.generateMonthlyReport(self.values['startDate'], self.values['endDate'])
        except DomainError as error:
            self.error_message, self.field_errors = str(error), getattr(error, 'field_errors', {})
            self.displayError()
            return
        self.displayReport(report)

    def displayReport(self, report: Report) -> None:
        if wants_html():
            flash('Monthly report generated successfully.', 'success')
            self.rendered_page = redirect(url_for('view_report', report_id=report.report_id), code=303)
        else:
            self.rendered_page = dict(ok=True, report=report.as_dict()), 201

    def displayError(self) -> None:
        self.rendered_page = error_response(self.error_message, 'manager', self.field_errors,
            values=self.values, template='reports/form.html', kind='monthly')
