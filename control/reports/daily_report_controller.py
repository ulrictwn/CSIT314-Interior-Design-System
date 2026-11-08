from datetime import date
from entity.reports.report import Report


class DailyReportController:
    def __init__(self, accountId=None, endDate=None):
        self.entity = Report(account_id=accountId)
        self.endDate = endDate

    def generateDailyReport(self, startDate: date) -> Report:
        return self.entity.generateReport('daily', startDate, self.endDate)
