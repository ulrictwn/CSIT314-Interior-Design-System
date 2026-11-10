from datetime import date
# entity/reports/report.py: saved report generation and snapshots.
from entity.reports.report import Report


class DailyReportController:
    def __init__(self, accountId=None, endDate=None):
        """Keep the Report operation entity and supplied end date."""
        self.entity = Report(account_id=accountId)
        self.endDate = endDate

    def generateDailyReport(self, startDate: date) -> Report:
        """Pass the request to Report.generateReport and return its result."""
        return self.entity.generateReport('daily', startDate, self.endDate)
