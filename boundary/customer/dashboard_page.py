from flask.views import MethodView
# boundary/portal.py: shared portal rendering and error displays.
from boundary.portal import optional_account_id, present
# control/customer/dashboard_controller.py: the boundary-to-entity request handler.
from control.customer.dashboard_controller import CustomerDashboardController


class CustomerDashboardPage(MethodView):
    def get(self):
        """Display saved-project totals from CustomerDashboardController."""
        owner = optional_account_id()
        return present(dict(ok=True, **CustomerDashboardController().summary(owner)),
                       'customer/dashboard.html','Dashboard','customer')
