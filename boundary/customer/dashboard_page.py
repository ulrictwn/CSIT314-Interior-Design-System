from flask.views import MethodView
from boundary.portal import optional_account_id, present
from control.customer.dashboard_controller import CustomerDashboardController


class CustomerDashboardPage(MethodView):
    def get(self):
        owner = optional_account_id()
        return present(dict(ok=True, **CustomerDashboardController().summary(owner)),
                       'customer/dashboard.html','Dashboard','customer')
