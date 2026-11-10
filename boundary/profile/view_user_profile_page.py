from flask import render_template
from flask.views import MethodView
# Ordinary input cleanup from boundary/validation.py; entities validate the values.
from boundary.validation import strip_input
# Controller used to relay this boundary request from control/profile/view_user_profile_controller.py.
from control.profile.view_user_profile_controller import ViewUserProfileController

# Entity used for saved data or return-value types from entity/profile/user_profile.py.
from entity.profile.user_profile import UserProfile


class ViewUserProfilePage(MethodView):

    def get(self, profile_id):
        """Pass the selected profile ID to the diagram onView event."""
        self.onView(profile_id)
        return self.rendered_page

    def onView(self, profileId: int) -> None:
        """Pass the stripped ID to the entity through the view controller.

        Uses boundary/validation.py, control/profile/view_user_profile_controller.py.
        """
        profileId = strip_input(profileId)
        profile = ViewUserProfileController().getUserProfile(profileId)
        if profile is None:
            self.rendered_page = render_template('error.html', code=404,
                message='User profile not found.', title='User Profile Not Found'), 404
        else:
            self.displayProfile(profile)

    def displayProfile(self, profile: UserProfile) -> None:
        """Render the selected profile details."""
        self.rendered_page = render_template(
            'profiles/detail.html', profile=profile, title=profile.name)
