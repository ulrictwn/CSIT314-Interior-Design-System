from flask import render_template, request
from flask.views import MethodView
from boundary.designer.context import request_values
from boundary.designer.presentation import wants_html


class StaffLoginPage(MethodView):
    """Route a staff form to the existing role-specific BCE login event."""
    def get(self):
        role = request.args.get('role','admin')
        if role not in ('admin','designer','manager'):
            role = 'admin'
        return render_template('auth/login.html',login_role=role,values={},errors={},title='Staff Sign In')

    def post(self):
        from boundary.auth.user_admin_login_page import UserAdminLoginPage
        from boundary.designer.interior_designer_login_page import InteriorDesignerLoginPage
        from boundary.platform_manager.platform_manager_login_page import PlatformManagerLoginPage
        values = request_values()
        role = values.get('staffRole','admin')
        pages = {'admin':UserAdminLoginPage,'designer':InteriorDesignerLoginPage,'manager':PlatformManagerLoginPage}
        if not isinstance(role,str) or role not in pages:
            message = 'Choose a supported staff role.'
            if not wants_html():
                return dict(ok=False,message=message,errors={'staffRole':[message]}),400
            return render_template('auth/login.html',login_role='admin',values=values,
                errors={'staffRole':[message]},error_message=message,title='Staff Sign In'),400
        page = pages[role]()
        event = page.onLogin
        event(values.get('username',''),values.get('password',''))
        if role == 'admin' and not wants_html() and hasattr(page,'error_message'):
            return dict(ok=False,message=page.error_message,errors=page.field_errors,
                        values={'username':values.get('username','')}),400
        return page.rendered_page
