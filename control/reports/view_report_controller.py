from entity.reports.report import Report


class ViewReportController:
    def getReport(self, reportId):
        return Report.getReport(reportId)
