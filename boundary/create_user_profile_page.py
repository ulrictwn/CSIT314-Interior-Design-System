from flask import render_template
from flask.views import MethodView

from boundary.create_user_profile_form import CreateUserProfileForm


class CreateUserProfilePage(MethodView):

    def get(self):
        form = CreateUserProfileForm()

        return render_template(
            "create_user_profile.html",
            form=form
        )