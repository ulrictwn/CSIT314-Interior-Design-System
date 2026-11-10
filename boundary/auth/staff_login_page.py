# boundary/validation.py: trims and checks submitted input fields.
from boundary.validation import strip_input
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
        role = strip_input(request.args.get('role', 'admin'))
        if role not in ('admin', 'designer', 'manager'):
            role = 'admin'
        return render_template('auth/login.html',login_role=role,values={},errors={},title='Staff Sign In')

    def post(self):
        """Check the selected role and call its imported boundary onLogin() method."""
        # boundary/auth/user_admin_login_page.py: provides the boundary classes used by these routes.
        from boundary.auth.user_admin_login_page import UserAdminLoginPage
        # boundary/designer/interior_designer_login_page.py: provides the boundary classes used by these routes.
        from boundary.designer.interior_designer_login_page import InteriorDesignerLoginPage
        # boundary/platform_manager/platform_manager_login_page.py: provides the boundary classes used by these routes.
        from boundary.platform_manager.platform_manager_login_page import PlatformManagerLoginPage
        values = request_values()
        role = strip_input(values.get('staffRole', 'admin'))
        pages = {'admin':UserAdminLoginPage,'designer':InteriorDesignerLoginPage,'manager':PlatformManagerLoginPage}
        if not isinstance(role, str) or role not in pages:
            message = 'Choose a supported staff role.'
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
