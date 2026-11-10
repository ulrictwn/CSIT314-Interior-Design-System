# boundary/validation.py: ordinary text cleanup only.
from boundary.validation import strip_input
from datetime import date
from flask import flash, redirect, url_for
from flask.views import MethodView
# boundary/designer/context.py: submitted values and signed-in account context.
from boundary.designer.context import request_values
# boundary/designer/presentation.py: HTML or JSON presentation choice.
from boundary.designer.presentation import wants_html
# boundary/portal.py: shared portal rendering and error displays.
from boundary.portal import optional_account_id, present, error_response
# boundary/reports/presentation.py: report date defaults and display labels.
from boundary.reports.presentation import default_dates
# control/reports/weekly_report_controller.py: the boundary-to-entity request handler.
from control.reports.weekly_report_controller import WeeklyReportController
# entity/reports/report.py: saved report generation and snapshots.
from entity.reports.report import Report
# infrastructure/errors.py: saved-data and validation errors.
from infrastructure.errors import DomainError


class WeeklyReportPage(MethodView):
    def get(self):
        """Display the weekly report form with initial date values."""
        return present(dict(ok=True, kind='weekly', values=default_dates('weekly')),
                       'reports/form.html', 'Generate Weekly Report', 'manager')

    def post(self):
        """Read the submitted request, run onGenerateWeeklyReport, and return the prepared response."""
        values = request_values()
        self.submitted_end_date = values.get('endDate')
        self.onGenerateWeeklyReport(values.get('startDate', ''))
        return self.rendered_page

    def onGenerateWeeklyReport(self, startDate: date) -> None:
        """Strip date input and display the saved report or the entity validation error."""
        self.values = dict(startDate=strip_input(startDate), endDate=strip_input(getattr(self, 'submitted_end_date', None)))
        try:
            controller = WeeklyReportController(accountId=optional_account_id(), endDate=self.values['endDate'])
            report = controller.generateWeeklyReport(self.values['startDate'])
        except DomainError as error:
            self.error_message, self.field_errors = str(error), getattr(error, 'field_errors', {})
            self.rendered_page = error_response(self.error_message, 'manager', self.field_errors,
                values=self.values, template='reports/form.html', kind='weekly')
            return
        self.displayReport(report)

    def displayReport(self, report: Report) -> None:
        """Redirect browsers to the saved report or return its JSON data."""
        if wants_html():
            flash('Weekly report generated successfully.', 'success')
            self.rendered_page = redirect(url_for('view_report', report_id=report.report_id), code=303)
        else:
            self.rendered_page = dict(ok=True, report=report.as_dict()), 201
