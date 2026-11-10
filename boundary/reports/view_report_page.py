import csv
import io
from flask import make_response
from flask.views import MethodView
# boundary/portal.py: shared portal rendering and error displays.
from boundary.portal import present, error_response
# control/reports/view_report_controller.py: the boundary-to-entity request handler.
from control.reports.view_report_controller import ViewReportController
# boundary/reports/presentation.py: report date defaults and display labels.
from boundary.reports.presentation import report_metrics
# boundary/validation.py: ordinary text cleanup only.
from boundary.validation import strip_input
# infrastructure/errors.py: saved-data and validation errors.
from infrastructure.errors import DomainError


class ViewReportPage(MethodView):
    def get(self,report_id):
        """Load and display a saved report through ViewReportController."""
        try:
            report = ViewReportController().getReport(strip_input(report_id))
        except DomainError as error:
            return error_response(str(error), 'manager', {'reportId': [str(error)]})
        if report is None:
            return error_response('Report not found.','manager',status=404)
        return present(dict(ok=True,report=report.as_dict(),metrics=report_metrics(report),kind=report.report_type,
            values=dict(startDate=report.start_date.isoformat(),endDate=report.end_date.isoformat())),
            'reports/form.html','Generate '+report.report_type.title()+' Report','manager')


class DownloadReportPage(MethodView):
    def get(self,report_id):
        """Load a saved report through ViewReportController and return its CSV."""
        try:
            report = ViewReportController().getReport(strip_input(report_id))
        except DomainError as error:
            return error_response(str(error), 'manager', {'reportId': [str(error)]})
        if report is None:
            return error_response('Report not found.','manager',status=404)
        stream = io.StringIO(newline='')
        writer = csv.writer(stream)
        writer.writerow(['Report type',report.report_type])
        writer.writerow(['Start date',report.start_date.isoformat()])
        writer.writerow(['End date',report.end_date.isoformat()])
        writer.writerow(['Generated at',report.as_dict()['generatedAt']])
        writer.writerow([])
        writer.writerow(['Metric','Total'])
        for name, key, detail in report_metrics(report):
            value = report.totals[key]
            writer.writerow([name, value if value is not None else 'No new IDPs'])
        writer.writerow([])
        current_format = 'topCategory' in report.totals
        writer.writerow(['IDP category', 'New IDPs'] if current_format else ['Platform area', 'Activity', 'Total'])
        for row in report.rows:
            writer.writerow([row['activity'], row['total']] if current_format else
                            [row['area'], row['activity'], row['total']])
        response = make_response(stream.getvalue())
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename="{report.report_type}-report-{report.report_id}.csv"'
        return response
