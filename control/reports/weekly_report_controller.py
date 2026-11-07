from datetime import date
from entity.reports.report import Report


class WeeklyReportController:
    def __init__(self, accountId=None):
        self.accountId = accountId

    def generateWeeklyReport(self, startDate: date) -> Report:
        report = Report(account_id=self.accountId)
        return report.generateReport('weekly', startDate, Report.periodEndDate('weekly', startDate))
