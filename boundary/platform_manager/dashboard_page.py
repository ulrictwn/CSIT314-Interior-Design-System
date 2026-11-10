from flask.views import MethodView
# boundary/portal.py: shared portal rendering and error displays.
from boundary.portal import present
# control/platform_manager/dashboard_controller.py: the boundary-to-entity request handler.
from control.platform_manager.dashboard_controller import PlatformManagerDashboardController


class PlatformManagerDashboardPage(MethodView):
    def get(self):
        """Display platform totals from PlatformManagerDashboardController."""
        return present(dict(ok=True, **PlatformManagerDashboardController().summary()),
            'platform_manager/dashboard.html','Platform Manager Dashboard','manager')
