from datetime import date
# entity/reports/report.py: saved report generation and snapshots.
from entity.reports.report import Report


class WeeklyReportController:
    def __init__(self, accountId=None, endDate=None):
        """Keep the Report operation entity and supplied end date."""
        self.entity = Report(account_id=accountId)
        self.endDate = endDate

    def generateWeeklyReport(self, startDate: date) -> Report:
        """Pass the request to Report.generateReport and return its result."""
        return self.entity.generateReport('weekly', startDate, self.endDate)
