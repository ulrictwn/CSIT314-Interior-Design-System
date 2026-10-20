from flask import render_template, request, redirect, url_for, flash
from boundary.base import Page
from boundary.forms import CreateUserProfileForm, ActionForm
from control.profile_controllers import (
    CreateUserProfileController, ViewUserProfileController, UpdateUserProfileController,
    SuspendUserProfileController, SearchUserProfileController, ProfileDirectoryController)
from infrastructure.errors import DomainError, AccessError


class UserProfilesPage(Page):
    def get(self):
        if not any(self.actor.has_permission(f'profile.{action}') for action in ('create', 'view', 'update', 'suspend', 'search')):
            raise AccessError('You do not have permission to access user profiles.')
        mode = request.args.get('mode', 'view')
        if mode == 'view' and not self.actor.has_permission('profile.view'):
            return render_template('profiles/index.html', profiles=None, mode=mode, title='User Profiles')
        profiles = ProfileDirectoryController(self.actor).listForAction(mode)
        return render_template('profiles/index.html', profiles=profiles, mode=mode,
                               title={'view': 'View', 'update': 'Update', 'suspend': 'Suspend'}.get(mode, 'View') + ' User Profiles')


class CreateUserProfilePage(Page):
    permission = 'profile.create'

    def get(self):
        return render_template('profiles/form.html', form=CreateUserProfileForm(),
                               title='Create User Profiles', editing=False, profile=None)

    def post(self):
        form = CreateUserProfileForm()
        if form.validate_on_submit():
            try:
                self.clickCreate(form.profileName.data, form.description.data, form.status.data, form.permissions.data)
                return self.displaySuccess()
            except AccessError:
                raise
            except DomainError as error:
                return self.displayError('profiles/form.html', form, str(error), title='Create User Profiles', editing=False, profile=None)
        return self.displayError('profiles/form.html', form, 'Please correct the errors below.',
                                 title='Create User Profiles', editing=False, profile=None)

    def clickCreate(self, profileName, description, status, permissions):
        return CreateUserProfileController(self.actor).createUserProfile(profileName, description, status, permissions)

    def displaySuccess(self):
        flash('User profile created successfully.', 'success')
        return redirect(url_for('user_profiles'))


class ViewUserProfilePage(Page):
    permission = 'profile.view'

    def get(self, profile_id):
        return self.onView(profile_id)

    def onView(self, profileId):
        return self.displayProfile(ViewUserProfileController(self.actor).getUserProfile(profileId))

    def displayProfile(self, profile):
        return render_template('profiles/detail.html', profile=profile, title=profile.name)


class UpdateUserProfilePage(Page):
    permission = 'profile.update'

    def get(self, profile_id):
        profile = UpdateUserProfileController(self.actor).getUserProfile(profile_id)
        form = CreateUserProfileForm(profileName=profile.name, description=profile.description,
                                     status=profile.status, permissions=profile.permissions)
        return render_template('profiles/form.html', form=form, profile=profile, editing=True, title='Update User Profiles')

    def post(self, profile_id):
        controller = UpdateUserProfileController(self.actor)
        profile = controller.getUserProfile(profile_id)
        form = CreateUserProfileForm()
        if form.validate_on_submit():
            try:
                self.onUpdate(profile_id, form.profileName.data, form.description.data, form.permissions.data, form.status.data)
                return self.displaySuccess()
            except AccessError:
                raise
            except DomainError as error:
                return self.displayError('profiles/form.html', form, str(error), profile=profile, editing=True, title='Update User Profiles')
        return self.displayError('profiles/form.html', form, 'Please correct the errors below.',
                                 profile=profile, editing=True, title='Update User Profiles')

    def onUpdate(self, profileId, profileName, description, permissions, status=None):
        return UpdateUserProfileController(self.actor).updateUserProfile(profileId, profileName, description, permissions, status)

    def displaySuccess(self):
        flash('User profile updated successfully.', 'success')
        return redirect(url_for('user_profiles'))


class SuspendUserProfilePage(Page):
    permission = 'profile.suspend'

    def get(self, profile_id):
        profile = SuspendUserProfileController(self.actor).getUserProfile(profile_id)
        return render_template('profiles/suspend.html', profile=profile, form=ActionForm(), title='Suspend User Profiles')

    def post(self, profile_id):
        profile = SuspendUserProfileController(self.actor).getUserProfile(profile_id)
        form = ActionForm()
        if form.validate_on_submit():
            try:
                self.onSuspend(profile_id)
                return self.displaySuccess()
            except AccessError:
                raise
            except DomainError as error:
                return self.displayError('profiles/suspend.html', form, str(error), profile=profile, title='Suspend User Profiles')
        return self.displayError('profiles/suspend.html', form, 'Please reload and try again.', profile=profile, title='Suspend User Profiles')

    def onSuspend(self, profileId):
        return SuspendUserProfileController(self.actor).suspendUserProfile(profileId)

    def displaySuccess(self):
        flash('User profile suspended successfully.', 'success')
        return redirect(url_for('user_profiles'))


class SearchUserProfilePage(Page):
    permission = 'profile.search'

    def get(self):
        self.keyword = request.args.get('q', '')
        controller = SearchUserProfileController(self.actor)

        if 'q' in request.args:
            try:
                self.onSearch(self.keyword)
            except AccessError:
                raise
            except DomainError as error:
                flash(str(error), 'error')
                self.displayResults(controller.listUserProfiles())
        else:
            self.displayResults(controller.listUserProfiles())

        return self.rendered_page

    def onSearch(self, keyword: str) -> None:
        self.keyword = keyword
        controller = SearchUserProfileController(self.actor)
        profiles = controller.searchUserProfiles(keyword)
        self.displayResults(profiles)

    def displayResults(self, profiles) -> None:
        self.rendered_page = render_template(
            'profiles/search.html',
            profiles=profiles,
            query=self.keyword,
            title='Search User Profiles'
        )
