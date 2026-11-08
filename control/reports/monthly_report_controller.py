from datetime import date
from entity.reports.report import Report


class MonthlyReportController:
    def __init__(self, accountId=None, endDate=None):
        self.entity = Report(account_id=accountId)
        self.endDate = endDate

    def generateMonthlyReport(self, startDate: date, endDate: date) -> Report:
        return self.entity.generateReport('monthly', startDate, endDate)
