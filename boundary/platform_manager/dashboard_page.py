from flask.views import MethodView
from boundary.portal import present
from control.platform_manager.dashboard_controller import PlatformManagerDashboardController


class PlatformManagerDashboardPage(MethodView):
    def get(self):
        return present(dict(ok=True, **PlatformManagerDashboardController().summary()),
            'platform_manager/dashboard.html','Platform Manager Dashboard','manager')
