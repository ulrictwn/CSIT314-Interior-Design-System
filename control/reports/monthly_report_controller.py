from datetime import date
# entity/reports/report.py: saved report generation and snapshots.
from entity.reports.report import Report


class MonthlyReportController:
    def __init__(self, accountId=None):
        """Create the Report operation entity for the signed-in account."""
        self.entity = Report(account_id=accountId)

    def generateMonthlyReport(self, startDate: date, endDate: date) -> Report:
        """Pass the request to Report.generateReport and return its result."""
        return self.entity.generateReport('monthly', startDate, endDate)
