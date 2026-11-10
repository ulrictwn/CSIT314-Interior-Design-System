# entity/reports/report.py: saved report generation and snapshots.
from entity.reports.report import Report


class PlatformManagerDashboardController:
    def summary(self):
        """Pass the request to Report.dashboard and return its result."""
        return Report.dashboard()
