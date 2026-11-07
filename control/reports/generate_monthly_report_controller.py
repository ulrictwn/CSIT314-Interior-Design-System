from entity.reports.report import Report


class GenerateMonthlyReportController:
    def generateMonthlyReport(self, startDate, endDate, accountId=None) -> Report:
        return Report.generateMonthlyReport(startDate, endDate, accountId)
