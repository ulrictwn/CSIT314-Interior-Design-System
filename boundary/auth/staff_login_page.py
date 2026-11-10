# boundary/validation.py: strips ordinary submitted text only.
from boundary.validation import strip_input
# control/auth/staff_login_controller.py: relays selector values to the account entity.
from control.auth.staff_login_controller import StaffLoginController
# infrastructure/errors.py: entity validation failures displayed by this boundary.
from infrastructure.errors import DomainError
from flask import render_template, request
from flask.views import MethodView
# boundary/designer/context.py: reads form/JSON values and the signed-in account.
from boundary.designer.context import request_values
# boundary/designer/presentation.py: chooses designer HTML/JSON responses.
from boundary.designer.presentation import wants_html


class StaffLoginPage(MethodView):
    """Route a staff form to the existing role-specific BCE login event."""
    def get(self):
        """Display the Staff login form with the selected supported portal role."""
        try:
            role = StaffLoginController().selectRole(strip_input(request.args.get('role', 'admin')))
        except DomainError:
            role = 'admin'
        return render_template('auth/login.html',login_role=role,values={},errors={},title='Staff Sign In')

    def post(self):
        """Pass the stripped selector to its controller and dispatch the role-specific login event."""
        # boundary/auth/user_admin_login_page.py: provides the boundary classes used by these routes.
        from boundary.auth.user_admin_login_page import UserAdminLoginPage
        # boundary/designer/interior_designer_login_page.py: provides the boundary classes used by these routes.
        from boundary.designer.interior_designer_login_page import InteriorDesignerLoginPage
        # boundary/platform_manager/platform_manager_login_page.py: provides the boundary classes used by these routes.
        from boundary.platform_manager.platform_manager_login_page import PlatformManagerLoginPage
        values = request_values()
        role = strip_input(values.get('staffRole', 'admin'))
        pages = {'admin':UserAdminLoginPage,'designer':InteriorDesignerLoginPage,'manager':PlatformManagerLoginPage}
        try:
            role = StaffLoginController().selectRole(role)
        except DomainError as error:
            message = str(error)
            if not wants_html():
                return dict(ok=False,message=message,errors={'staffRole':[message]}),400
            return render_template('auth/login.html',login_role='admin',values=values,
                errors={'staffRole':[message]},error_message=message,title='Staff Sign In'),400
        page = pages[role]()
        page.onLogin(values.get('username', ''), values.get('password', ''))
        if role == 'admin' and not wants_html() and hasattr(page,'error_message'):
            return dict(ok=False,message=page.error_message,errors=page.field_errors,
                        values={'username':values.get('username','')}),400
        return page.rendered_page
