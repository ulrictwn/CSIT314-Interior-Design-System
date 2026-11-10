# entity/reports/report.py: saved report generation and snapshots.
from entity.reports.report import Report


class ViewReportController:
    def getReport(self, reportId):
        """Pass the request to Report.getReport and return its result."""
        return Report.getReport(reportId)
