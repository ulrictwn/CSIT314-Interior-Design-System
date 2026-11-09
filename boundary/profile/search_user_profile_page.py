from control.profile.profile_controllers import ProfileDirectoryController
from flask import render_template, request, flash
from flask.views import MethodView
from boundary.validation import strip_input
from control.profile.search_user_profile_controller import SearchUserProfileController
from infrastructure.errors import DomainError

from entity.profile.user_profile import UserProfile


class SearchUserProfilePage(MethodView):

    def get(self):
        self.keyword = request.args.get('q', '')
        if 'q' in request.args:
            self.onSearch(self.keyword)
        else:
            self.displayResults(ProfileDirectoryController().listForAction())
        return self.rendered_page

    def onSearch(self, keyword: str) -> None:
        self.keyword = keyword
        controller = SearchUserProfileController()
        try:
            keyword = strip_input(keyword)
            profiles = controller.searchUserProfiles(keyword)
        except DomainError as error:
            flash(str(error), 'error')
            profiles = ProfileDirectoryController().listForAction()
        self.displayResults(profiles)

    def displayResults(self, profiles: list[UserProfile]) -> None:
        self.rendered_page = render_template(
            'profiles/search.html', profiles=profiles, query=self.keyword,
            title='Search User Profiles')
