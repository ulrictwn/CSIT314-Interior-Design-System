# boundary/validation.py: input cleanup and field checks.
from boundary.validation import strip_input, validate_report_dates
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
# control/reports/monthly_report_controller.py: the boundary-to-entity request handler.
from control.reports.monthly_report_controller import MonthlyReportController
# entity/reports/report.py: saved report generation and snapshots.
from entity.reports.report import Report
# infrastructure/errors.py: saved-data and validation errors.
from infrastructure.errors import DomainError


class MonthlyReportPage(MethodView):
    def get(self):
        """Display the monthly report form with initial date values."""
        return present(dict(ok=True, kind='monthly', values=default_dates('monthly')),
                       'reports/form.html', 'Generate Monthly Report', 'manager')

    def post(self):
        """Read the submitted request, run onGenerateMonthlyReport, and return the prepared response."""
        values = request_values()
        self.onGenerateMonthlyReport(values.get('startDate', ''), values.get('endDate', ''))
        return self.rendered_page

    def onGenerateMonthlyReport(self, startDate: date, endDate: date) -> None:
        """Check the selected dates, then request a saved report through the report controller."""
        self.values = dict(startDate=strip_input(startDate), endDate=strip_input(endDate))
        try:
            start, end = validate_report_dates('monthly', self.values['startDate'], self.values['endDate'])
            controller = MonthlyReportController(accountId=optional_account_id())
            report = controller.generateMonthlyReport(start, end)
        except DomainError as error:
            self.error_message, self.field_errors = str(error), getattr(error, 'field_errors', {})
            self.rendered_page = error_response(self.error_message, 'manager', self.field_errors,
                values=self.values, template='reports/form.html', kind='monthly')
            return
        self.displayReport(report)

    def displayReport(self, report: Report) -> None:
        """Redirect browsers to the saved report or return its JSON data."""
        if wants_html():
            flash('Monthly report generated successfully.', 'success')
            self.rendered_page = redirect(url_for('view_report', report_id=report.report_id), code=303)
        else:
            self.rendered_page = dict(ok=True, report=report.as_dict()), 201
