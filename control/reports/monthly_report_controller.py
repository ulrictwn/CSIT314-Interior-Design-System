from datetime import date
from entity.reports.report import Report


class MonthlyReportController:
    def __init__(self, accountId=None):
        self.accountId = accountId

    def generateMonthlyReport(self, startDate: date, endDate: date) -> Report:
        report = Report(account_id=self.accountId)
        return report.generateReport('monthly', startDate, endDate)
