from __future__ import annotations

from typing import TYPE_CHECKING
from flask import render_template
from boundary.base import Page
from control.profile.view_user_profile_controller import ViewUserProfileController

if TYPE_CHECKING:
    from entity.profile.user_profile import UserProfile


class ViewUserProfilePage(Page):
    permission = 'profile.view'

    def get(self, profile_id):
        self.onView(profile_id)
        return self.rendered_page

    def onView(self, profileId: int) -> None:
        profile = ViewUserProfileController(self.actor).getUserProfile(profileId)
        if profile is None:
            self.displayError()
        else:
            self.displayProfile(profile)

    def displayProfile(self, profile: UserProfile) -> None:
        self.rendered_page = render_template(
            'profiles/detail.html', profile=profile, title=profile.name)

    def displayError(self) -> None:
        self.rendered_page = render_template(
            'error.html', code=404, message='User profile not found.',
            title='User Profile Not Found'), 404
