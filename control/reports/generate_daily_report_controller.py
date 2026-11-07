from entity.reports.report import Report


class GenerateDailyReportController:
    def generateDailyReport(self, startDate, endDate, accountId=None) -> Report:
        return Report.generateDailyReport(startDate, endDate, accountId)
