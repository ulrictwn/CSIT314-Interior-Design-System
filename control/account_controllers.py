import re
from email_validator import validate_email, EmailNotValidError
from control.base import Controller, required
from entity.user_account import UserAccount
from entity.user_profile import UserProfile
from infrastructure.database import db
from infrastructure.errors import DomainError, NotFoundError


def email_address(value):
    try:
        return validate_email(required(value, 'Email', 254), check_deliverability=False).normalized.lower()
    except EmailNotValidError as error:
        raise DomainError('Enter a valid email address.') from error


def password_value(value):
    if not isinstance(value, str) or not 12 <= len(value) <= 128:
        raise DomainError('Passwords must contain between 12 and 128 characters.')
    return value


def username_value(value):
    value = required(value, 'Username', 80)
    if not re.fullmatch(r'[A-Za-z0-9_.-]{3,80}', value):
        raise DomainError('Username must contain 3–80 letters, numbers, dots, underscores, or hyphens.')
    return value


class AccountController(Controller):
    def get(self, accountId, permission):
        self.require(permission)
        account = UserAccount.getUserAccount(accountId)
        if account is None:
            raise NotFoundError('User account not found.')
        return account

    def activeProfiles(self, permission):
        self.require(permission)
        return [profile for profile in UserProfile.listUserProfiles() if profile.status == 'Active']

    def validate_details(self, fullName, email, profileId, exclude_id=None):
        fullName, email = required(fullName, 'Full name', 120), email_address(email)
        profile = UserProfile.getUserProfile(profileId)
        if profile is None or profile.status != 'Active':
            raise DomainError('Assign an active user profile.')
        query = db.select(UserAccount.account_id).where(db.func.lower(UserAccount.email) == email)
        if exclude_id is not None:
            query = query.where(UserAccount.account_id != exclude_id)
        if db.session.execute(query.limit(1)).first():
            raise DomainError('The email is already registered.')
        return fullName, email


class CreateUserAccountController(AccountController):
    def userAccountExists(self, username):
        self.require('account.create')
        return UserAccount.userAccountExists(username)

    def createUserAccount(self, username, fullName, email, phoneNumber, profileId):
        self.require('account.create')
        username = username_value(username)
        fullName, email = self.validate_details(fullName, email, profileId)
        phoneNumber = required(phoneNumber, 'Phone number', 40)
        if not re.fullmatch(r'\+?[0-9][0-9 ()-]{5,38}', phoneNumber):
            raise DomainError('Enter a valid phone number.')
        if self.userAccountExists(username):
            raise DomainError('The username is already registered.')
        if not UserAccount.createUserAccount(username, fullName, email, phoneNumber, profileId):
            raise DomainError('The username or email is already registered.')
        return True


class ViewUserAccountController(AccountController):
    def getUserAccount(self, accountId):
        return self.get(accountId, 'account.view')

    def listUserAccounts(self):
        self.require('account.view')
        return UserAccount.searchUserAccounts()


class UpdateUserAccountController(AccountController):
    def getUserAccount(self, accountId):
        return self.get(accountId, 'account.update')

    def updateUserAccount(self, accountId, fullName, email, profileId):
        self.getUserAccount(accountId)
        fullName, email = self.validate_details(fullName, email, profileId, accountId)
        if not UserAccount.updateUserAccount(accountId, fullName, email, profileId):
            raise DomainError('The email is already registered.')
        return True


class SuspendUserAccountController(AccountController):
    def getUserAccount(self, accountId):
        return self.get(accountId, 'account.suspend')

    def suspendUserAccount(self, accountId):
        self.getUserAccount(accountId)
        return UserAccount.suspendUserAccount(accountId)


class SearchUserAccountController(AccountController):
    def searchUserAccounts(self, keyword=''):
        self.require('account.search')
        if not isinstance(keyword, str) or len(keyword) > 200:
            raise DomainError('Search text must contain at most 200 characters.')
        return UserAccount.searchUserAccounts(keyword)


class AccountDirectoryController(AccountController):
    def listForAction(self, mode='view'):
        permission = {'view': 'account.view', 'update': 'account.update', 'suspend': 'account.suspend'}.get(mode)
        if permission is None:
            raise DomainError('Choose a supported account operation.')
        self.require(permission)
        return UserAccount.searchUserAccounts()
