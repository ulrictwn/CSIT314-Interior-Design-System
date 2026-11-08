"""Shared HTML/JSON presentation for the customer and platform manager pages."""
from flask import g, render_template, request, session, url_for
from boundary.designer.presentation import wants_html


def optional_account_id():
    return session.get('account_id')


def present(payload, template, title, portal, status=200):
    if not wants_html():
        return payload, status
    owner = optional_account_id()

    def link(endpoint, **kwargs):
        if owner and 'login' not in endpoint and 'logout' not in endpoint:
            kwargs.setdefault('accountId', owner)
        return url_for(endpoint, **kwargs)

    return render_template(template, data=payload, title=title, portal=portal, ui_url=link,
        owner_id=owner, current_user=g.get('current_user'), active_endpoint=request.endpoint,
        values=payload.get('values', {}), errors=payload.get('errors', {}),
        error_message=payload.get('message') if not payload.get('ok') else None), status


def error_response(message, portal, errors=None, status=400, values=None, template='portal/error.html', **extra):
    return present(dict(ok=False, message=message, errors=errors or {}, values=values or {}, **extra),
                   template, 'Please check the details', portal, status)
