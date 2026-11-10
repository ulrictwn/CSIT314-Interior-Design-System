"""HTML presentation for the designer boundaries, with the JSON interface retained."""
from flask import flash, g, has_request_context, redirect, render_template, request, url_for
# boundary/designer/context.py: reads form/JSON values and the signed-in account.
from boundary.designer.context import account_id
# control/categories/search_category_controller.py: provides the controller used to communicate with its entity.
from control.categories.search_category_controller import SearchCategoryController


def wants_html():
    """Choose HTML or JSON from the request format, body and Accept header."""
    if not has_request_context() or request.is_json:
        return False
    representation = request.args.get('format')
    if representation in ('html', 'json'):
        return representation == 'html'
    return request.accept_mimetypes.best_match(['text/html', 'application/json']) == 'text/html'


def present(payload, status=200):
    """Prepare the designer template or JSON response for the current operation."""
    if not wants_html():
        return payload, status
    endpoint = request.endpoint or ''
    if endpoint == 'interior_designer_login':
        return render_template('auth/login.html', login_role='designer',
            values=payload.get('values', {}), errors=payload.get('errors', {}),
            error_message=payload.get('message') if not payload.get('ok') else None,
            title='Interior Designer Sign In'), status
    profile, project = payload.get('profile'), payload.get('project')
    owner = (profile or project or {}).get('accountId') or payload.get('accountId')
    if not owner:
        owner = account_id()
    def link(name, **kwargs):
        """Build a page link with the current account context."""
        if owner and name not in ('login', 'interior_designer_login', 'interior_designer_logout'):
            kwargs.setdefault('accountId', owner)
        return url_for(name, **kwargs)
    phase = 'past' if 'past' in endpoint else 'new'
    phase_label = 'Past' if phase == 'past' else 'New'
    # Navigation mode chooses a row-action display; unknown modes show Search.
    mode = {'view': 'view', 'search': 'search', 'update': 'update', 'delete': 'delete'}.get(
        request.values.get('mode', 'search'), 'search')
    if request.method == 'POST' and payload.get('ok') and 'message' in payload:
        flash(payload['message'], 'success')
        if endpoint in ('create_company_profile', 'update_company_profile'):
            target = link('view_company_profile')
        elif endpoint == 'delete_company_profile':
            target = link('search_company_profile')
        elif endpoint.startswith(('create_', 'update_')) and endpoint.endswith('_project'):
            project_id = (project or {}).get('projectId') or (request.view_args or {}).get('project_id')
            target = link('view_'+phase+'_project', project_id=project_id)
        else:
            target = link(phase+'_projects', mode='delete')
        return redirect(target, code=303)
    context = dict(data=payload, values=payload.get('values', {}), errors=payload.get('errors', {}),
        error_message=payload.get('message') if not payload.get('ok') else None,
        owner_id=owner, ui_url=link, phase=phase, phase_label=phase_label, mode=mode,
        current_user=g.get('current_user'), active_endpoint=endpoint,
        property_types=['Apartment', 'Condominium', 'Landed property', '3-room HDB', '4-room HDB', '5-room HDB'])
    if endpoint.startswith(('create_', 'update_')) and endpoint.endswith('_project'):
        context['categories'] = SearchCategoryController().searchCategories('')
    if status == 404 or (status >= 400 and not payload.get('values') and 'search' not in endpoint
                          and endpoint not in ('new_projects', 'past_projects')):
        template = 'designer/error.html'
        context['title'] = 'Unable to open this page'
    elif endpoint == 'designer_dashboard':
        template, context['title'] = 'designer/dashboard.html', 'Dashboard'
    elif endpoint in ('create_company_profile', 'update_company_profile'):
        template = 'company/form.html'
        context.update(editing=endpoint.startswith('update'), title='Update Company Details' if endpoint.startswith('update') else 'Create Company Profile')
    elif endpoint == 'view_company_profile':
        template, context['title'] = 'company/detail.html', 'View Company Details'
    elif endpoint == 'delete_company_profile':
        template, context['title'] = 'company/delete.html', 'Delete Company Profile'
    elif endpoint == 'search_company_profile':
        template, context['title'] = 'company/search.html', 'Search Company Profile'
    elif endpoint.startswith(('create_', 'update_')):
        template = 'projects/form.html'
        context.update(editing=endpoint.startswith('update'), title=('Update ' if endpoint.startswith('update') else 'Create ')+phase_label+' Interior Design Project')
    elif endpoint.startswith('view_'):
        template, context['title'] = 'projects/detail.html', 'View '+phase_label+' Interior Design Project'
    elif endpoint.startswith('delete_'):
        template, context['title'] = 'projects/delete.html', 'Delete '+phase_label+' Interior Design Project'
    else:
        template = 'projects/index.html'
        context['title'] = mode.title()+' '+phase_label+' Interior Design Projects'
    return render_template(template, **context), status
