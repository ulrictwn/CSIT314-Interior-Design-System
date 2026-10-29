from __future__ import annotations

from typing import TYPE_CHECKING
from flask import render_template, request, flash
from boundary.base import Page
from control.profile.search_user_profile_controller import SearchUserProfileController
from infrastructure.errors import DomainError, AccessError

if TYPE_CHECKING:
    from entity.profile.user_profile import UserProfile


class SearchUserProfilePage(Page):
    permission = 'profile.search'

    def get(self):
        self.keyword = request.args.get('q', '')
        if 'q' in request.args:
            self.onSearch(self.keyword)
        else:
            self.displayResults(SearchUserProfileController(self.actor).listUserProfiles())
        return self.rendered_page

    def onSearch(self, keyword: str) -> None:
        self.keyword = keyword
        controller = SearchUserProfileController(self.actor)
        try:
            profiles = controller.searchUserProfiles(keyword)
        except AccessError:
            raise
        except DomainError as error:
            flash(str(error), 'error')
            profiles = controller.listUserProfiles()
        self.displayResults(profiles)

    def displayResults(self, profiles: list[UserProfile]) -> None:
        self.rendered_page = render_template(
            'profiles/search.html', profiles=profiles, query=self.keyword,
            title='Search User Profiles')
