"""Basic session, portal-role, and ownership checks for the four portals."""
from flask import g, redirect, request, session, url_for
from entity.accounts.user_account import UserAccount
from entity.projects.interior_design_project import InteriorDesignProject
from infrastructure.errors import AccessDeniedError

LOGIN_ENDPOINTS = {
    'admin': 'login', 'designer': 'interior_designer_login',
    'customer': 'customer_login', 'manager': 'platform_manager_login',
}
PUBLIC_ENDPOINTS = {'static', 'home', 'login', 'staff_login', 'interior_designer_login',
                    'customer_login', 'platform_manager_login'}


def load_account():
    account_id = session.get('account_id')
    account = UserAccount.getUserAccount(account_id) if account_id else None
    g.current_user = account if account and account.portalRole() else None
    if account_id and g.current_user is None:
        session.clear()


def require_portal_access():
    """Use saved identity, never a submitted accountId, for protected requests."""
    if request.endpoint is None or request.endpoint in PUBLIC_ENDPOINTS:
        return None
    path = request.path
    if path == '/designer' or path.startswith('/designer/'):
        role = 'designer'
    elif path == '/customer' or path.startswith('/customer/'):
        role = 'customer'
    elif path == '/manager' or path.startswith('/manager/'):
        role = 'manager'
    else:
        role = 'admin'
    account = g.current_user
    if account is None:
        return redirect(url_for(LOGIN_ENDPOINTS[role]))
    if account.portalRole() != role:
        raise AccessDeniedError('Your account cannot access this portal.')
    if role != 'admin':
        supplied_ids = request.args.getlist('accountId') + request.form.getlist('accountId')
        payload = request.get_json(silent=True) if request.is_json else None
        if isinstance(payload, dict) and 'accountId' in payload:
            supplied_ids.append(payload['accountId'])
        if any(not isinstance(value, str) or value.strip() != account.account_id for value in supplied_ids):
            raise AccessDeniedError('Use your signed-in account for this operation.')
    if role == 'designer' and 'project_id' in (request.view_args or {}):
        InteriorDesignProject.checkOwnership(account.account_id, request.view_args['project_id'])
    return None
