from flask.views import MethodView
from boundary.portal import optional_account_id, present, error_response
from control.customer.dashboard_controller import CustomerDashboardController
from infrastructure.errors import DomainError


class CustomerDashboardPage(MethodView):
    def get(self):
        try:
            owner = optional_account_id()
        except DomainError as error:
            return error_response(str(error),'customer')
        return present(dict(ok=True, **CustomerDashboardController().summary(owner)),
                       'customer/dashboard.html','Dashboard','customer')
