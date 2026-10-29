from flask import g, render_template, flash
from flask.views import MethodView
from infrastructure.database import db
from infrastructure.errors import AccessError


class Page(MethodView):
    permission = None

    @property
    def actor(self):
        return g.get('profile_actor')

    def dispatch_request(self, *args, **kwargs):
        if self.actor is None:
            raise AccessError('Please sign in with an active User Admin account.')
        if self.permission and not self.actor.has_permission(self.permission):
            raise AccessError('You do not have permission to access this page.')
        return super().dispatch_request(*args, **kwargs)

    def displayError(self, template, form=None, error_message=None, **context):
        db.session.rollback()
        if error_message:
            flash(error_message, 'error')
        return render_template(template, form=form, **context), 400
