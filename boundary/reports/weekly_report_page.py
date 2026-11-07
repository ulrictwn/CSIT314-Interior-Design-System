from datetime import date
from flask import flash, redirect, url_for
from flask.views import MethodView
from boundary.designer.context import request_values
from boundary.designer.presentation import wants_html
from boundary.portal import optional_account_id, present, error_response
from boundary.reports.validation import default_dates, validate_report_dates
from control.reports.weekly_report_controller import WeeklyReportController
from entity.reports.report import Report
from infrastructure.errors import DomainError


class WeeklyReportPage(MethodView):
    def get(self):
        return present(dict(ok=True, kind='weekly', values=default_dates('weekly')),
                       'reports/form.html', 'Generate Weekly Report', 'manager')

    def post(self):
        values = request_values()
        self.submitted_end_date = values.get('endDate')
        self.onGenerateWeeklyReport(values.get('startDate', ''))
        return self.rendered_page

    def onGenerateWeeklyReport(self, startDate: date) -> None:
        self.values = dict(startDate=startDate, endDate=getattr(self, 'submitted_end_date', None))
        try:
            start, end = validate_report_dates('weekly', startDate, getattr(self, 'submitted_end_date', None))
            self.values = dict(startDate=start.isoformat(), endDate=end.isoformat())
            controller = WeeklyReportController(accountId=optional_account_id())
            report = controller.generateWeeklyReport(start)
        except DomainError as error:
            self.error_message, self.field_errors = str(error), getattr(error, 'field_errors', {})
            self.displayError()
            return
        self.displayReport(report)

    def displayReport(self, report: Report) -> None:
        if wants_html():
            flash('Weekly report generated successfully.', 'success')
            self.rendered_page = redirect(url_for('view_report', report_id=report.report_id), code=303)
        else:
            self.rendered_page = dict(ok=True, report=report.as_dict()), 201

    def displayError(self) -> None:
        self.rendered_page = error_response(self.error_message, 'manager', self.field_errors,
            values=self.values, template='reports/form.html', kind='weekly')
