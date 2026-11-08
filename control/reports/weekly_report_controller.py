from datetime import date
from entity.reports.report import Report


class WeeklyReportController:
    def __init__(self, accountId=None, endDate=None):
        self.entity = Report(account_id=accountId)
        self.endDate = endDate

    def generateWeeklyReport(self, startDate: date) -> Report:
        return self.entity.generateReport('weekly', startDate, self.endDate)
