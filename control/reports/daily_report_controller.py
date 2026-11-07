from datetime import date
from entity.reports.report import Report


class DailyReportController:
    def __init__(self, accountId=None):
        self.accountId = accountId

    def generateDailyReport(self, startDate: date) -> Report:
        report = Report(account_id=self.accountId)
        return report.generateReport('daily', startDate, startDate)
