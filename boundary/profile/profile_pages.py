from flask import render_template, request
from flask.views import MethodView
from control.profile.profile_controllers import ProfileDirectoryController
from infrastructure.errors import DomainError


class UserProfilesPage(MethodView):
    def get(self):
        mode = request.args.get('mode', 'view')
        if mode not in ('view', 'update', 'suspend'):
            raise DomainError('Choose a supported profile operation.')
        profiles = ProfileDirectoryController().listForAction()
        return render_template('profiles/index.html', profiles=profiles, mode=mode,
            title=mode.title() + ' User Profiles')
