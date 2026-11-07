from entity.reports.report import Report


class GenerateWeeklyReportController:
    def generateWeeklyReport(self, startDate, endDate, accountId=None) -> Report:
        return Report.generateWeeklyReport(startDate, endDate, accountId)
