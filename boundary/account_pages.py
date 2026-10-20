from flask import render_template, request, redirect, url_for, flash
from boundary.base import Page
from boundary.forms import CreateUserAccountForm, UpdateUserAccountForm, ActionForm
from control.account_controllers import (CreateUserAccountController, ViewUserAccountController,
    UpdateUserAccountController, SuspendUserAccountController, SearchUserAccountController, AccountDirectoryController)
from infrastructure.errors import DomainError, AccessError


class UserAccountsPage(Page):
    def get(self):
        mode = request.args.get('mode', 'view')
        if not any(self.actor.has_permission('account.'+action) for action in ('create','view','update','suspend','search')):
            raise AccessError('You do not have permission to access user accounts.')
        accounts = None if mode == 'view' and not self.actor.has_permission('account.view') else AccountDirectoryController(self.actor).listForAction(mode)
        return render_template('accounts/index.html', accounts=accounts, mode=mode, title=mode.title()+' User Accounts')


class CreateUserAccountPage(Page):
    permission = 'account.create'

    def form(self):
        form = CreateUserAccountForm()
        form.profile_id.choices = [(p.profile_id, p.name) for p in CreateUserAccountController(self.actor).activeProfiles(self.permission)]
        return form

    def get(self):
        return render_template('accounts/form.html', form=self.form(), editing=False, account=None, title='Create User Accounts')

    def post(self):
        form = self.form()
        if form.validate_on_submit():
            try:
                self.clickCreate(form.username.data, form.password.data, form.full_name.data,
                                 form.email.data, form.phone_number.data, form.profile_id.data)
                return self.rendered_page
            except AccessError:
                raise
            except DomainError as error:
                return self.displayError('accounts/form.html', form, str(error), editing=False, account=None, title='Create User Accounts')
        return self.displayError('accounts/form.html', form, 'Please correct the errors below.', editing=False, account=None, title='Create User Accounts')

    def clickCreate(self, username, password, fullName, email, phoneNumber, profileId) -> None:
        CreateUserAccountController(self.actor).createUserAccount(username, password, fullName, email, phoneNumber, profileId)
        self.displaySuccess()

    def displaySuccess(self) -> None:
        flash('User account created successfully.', 'success')
        self.rendered_page = redirect(url_for('user_accounts'))


class ViewUserAccountPage(Page):
    permission = 'account.view'

    def get(self, account_id):
        self.onView(account_id)
        return self.rendered_page

    def onView(self, accountId) -> None:
        self.displayAccount(ViewUserAccountController(self.actor).getUserAccount(accountId))

    def displayAccount(self, account) -> None:
        self.rendered_page = render_template('accounts/detail.html', account=account, title='View User Accounts')


class UpdateUserAccountPage(Page):
    permission = 'account.update'

    def form(self, account=None):
        form = UpdateUserAccountForm(obj=account)
        form.profile_id.choices = [(p.profile_id, p.name) for p in UpdateUserAccountController(self.actor).activeProfiles(self.permission)]
        return form

    def get(self, account_id):
        account = UpdateUserAccountController(self.actor).getUserAccount(account_id)
        return render_template('accounts/form.html', form=self.form(account), account=account, editing=True, title='Update User Accounts')

    def post(self, account_id):
        account = UpdateUserAccountController(self.actor).getUserAccount(account_id)
        form = self.form()
        if form.validate_on_submit():
            try:
                self.onUpdate(account_id, form.full_name.data, form.email.data, form.profile_id.data)
                return self.rendered_page
            except AccessError:
                raise
            except DomainError as error:
                return self.displayError('accounts/form.html', form, str(error), account=account, editing=True, title='Update User Accounts')
        return self.displayError('accounts/form.html', form, 'Please correct the errors below.', account=account, editing=True, title='Update User Accounts')

    def onUpdate(self, accountId, fullName, email, profileId) -> None:
        UpdateUserAccountController(self.actor).updateUserAccount(accountId, fullName, email, profileId)
        self.displaySuccess()

    def displaySuccess(self) -> None:
        flash('User account updated successfully.', 'success')
        self.rendered_page = redirect(url_for('user_accounts'))


class SuspendUserAccountPage(Page):
    permission = 'account.suspend'

    def get(self, account_id):
        account = SuspendUserAccountController(self.actor).getUserAccount(account_id)
        return render_template('accounts/suspend.html', account=account, form=ActionForm(), title='Suspend User Accounts')

    def post(self, account_id):
        account = SuspendUserAccountController(self.actor).getUserAccount(account_id)
        form = ActionForm()
        if form.validate_on_submit():
            try:
                self.onSuspend(account_id)
                return self.rendered_page
            except AccessError:
                raise
            except DomainError as error:
                return self.displayError('accounts/suspend.html', form, str(error), account=account, title='Suspend User Accounts')
        return self.displayError('accounts/suspend.html', form, 'Reload the confirmation form and try again.', account=account, title='Suspend User Accounts')

    def onSuspend(self, accountId) -> None:
        SuspendUserAccountController(self.actor).suspendUserAccount(accountId)
        self.displaySuccess()

    def displaySuccess(self) -> None:
        flash('User account suspended successfully.', 'success')
        self.rendered_page = redirect(url_for('user_accounts'))


class SearchUserAccountPage(Page):
    permission = 'account.search'

    def get(self):
        self.keyword = request.args.get('q', '')
        try:
            self.onSearch(self.keyword)
        except AccessError:
            raise
        except DomainError as error:
            flash(str(error), 'error')
            self.displayResults([])
        return self.rendered_page

    def onSearch(self, keyword) -> None:
        self.keyword = keyword
        self.displayResults(SearchUserAccountController(self.actor).searchUserAccounts(keyword))

    def displayResults(self, accounts) -> None:
        self.rendered_page = render_template('accounts/search.html', query=self.keyword, accounts=accounts, title='Search User Accounts')
