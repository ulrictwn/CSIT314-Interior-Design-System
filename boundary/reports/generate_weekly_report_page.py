from flask import flash, redirect, url_for
from flask.views import MethodView
from boundary.designer.context import request_values
from boundary.designer.presentation import wants_html
from boundary.portal import optional_account_id, present, error_response
from boundary.reports.validation import default_dates, validate_report_dates
from control.reports.generate_weekly_report_controller import GenerateWeeklyReportController
from infrastructure.errors import DomainError


class GenerateWeeklyReportPage(MethodView):
    def get(self):
        return present(dict(ok=True,kind='weekly',values=default_dates('weekly')),
                       'reports/form.html','Generate Weekly Report','manager')

    def post(self):
        values = request_values()
        self.onGenerate(values.get('startDate',''),values.get('endDate',''))
        return self.rendered_page

    def onGenerate(self,startDate: str,endDate: str) -> None:
        self.values = dict(startDate=startDate,endDate=endDate)
        try:
            start,end = validate_report_dates('weekly',startDate,endDate)
            owner = optional_account_id()
            self.report = GenerateWeeklyReportController().generateWeeklyReport(start,end,owner)
        except DomainError as error:
            self.error_message, self.field_errors = str(error),getattr(error,'field_errors',{})
            self.displayError()
            return
        self.displayReport()

    def displayReport(self) -> None:
        if wants_html():
            flash('Weekly report generated successfully.','success')
            self.rendered_page = redirect(url_for('view_report',report_id=self.report.report_id),code=303)
        else:
            self.rendered_page = dict(ok=True,report=self.report.as_dict()),201

    def displayError(self) -> None:
        self.rendered_page = error_response(self.error_message,'manager',self.field_errors,
            values=self.values,template='reports/form.html',kind='weekly')
