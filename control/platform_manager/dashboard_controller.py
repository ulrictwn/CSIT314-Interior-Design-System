from entity.reports.report import Report


class PlatformManagerDashboardController:
    def summary(self):
        return Report.dashboard()
