import csv
import io
from flask import make_response
from flask.views import MethodView
from boundary.portal import present, error_response
from control.reports.view_report_controller import ViewReportController


class ViewReportPage(MethodView):
    def get(self,report_id):
        report = ViewReportController().getReport(report_id)
        if report is None:
            return error_response('Report not found.','manager',status=404)
        return present(dict(ok=True,report=report.as_dict(),kind=report.report_type,
            values=dict(startDate=report.start_date.isoformat(),endDate=report.end_date.isoformat())),
            'reports/form.html','Generate '+report.report_type.title()+' Report','manager')


class DownloadReportPage(MethodView):
    def get(self,report_id):
        report = ViewReportController().getReport(report_id)
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
        for name,key in [('Successful logins','successfulLogins'),('New registrations','newRegistrations'),('Projects created','projectsCreated')]:
            writer.writerow([name,report.totals[key]])
        writer.writerow([])
        writer.writerow(['Platform area','Activity','Total'])
        for row in report.rows:
            writer.writerow([row['area'],row['activity'],row['total']])
        response = make_response(stream.getvalue())
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename="{report.report_type}-report-{report.report_id}.csv"'
        return response
