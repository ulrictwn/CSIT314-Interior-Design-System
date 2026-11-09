from flask import render_template
from flask.views import MethodView
from control.profile.view_user_profile_controller import ViewUserProfileController

from entity.profile.user_profile import UserProfile


class ViewUserProfilePage(MethodView):

    def get(self, profile_id):
        self.onView(profile_id)
        return self.rendered_page

    def onView(self, profileId: int) -> None:
        profile = ViewUserProfileController().getUserProfile(profileId)
        if profile is None:
            self.rendered_page = render_template('error.html', code=404,
                message='User profile not found.', title='User Profile Not Found'), 404
        else:
            self.displayProfile(profile)

    def displayProfile(self, profile: UserProfile) -> None:
        self.rendered_page = render_template(
            'profiles/detail.html', profile=profile, title=profile.name)
