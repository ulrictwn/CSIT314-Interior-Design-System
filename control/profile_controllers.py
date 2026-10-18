from control.base import Controller, required
from entity.user_profile import UserProfile
from infrastructure.errors import DomainError, NotFoundError
from infrastructure.permissions import PERMISSION_OPTIONS


def validate_profile(profileName, description, status, permissions):
    name = required(profileName, 'Profile name', 100)
    description = required(description, 'Description')
    if status not in ('Active', 'Suspended'):
        raise DomainError('Choose Active or Suspended.')
    if not isinstance(permissions, list) or any(
            not isinstance(p, str) or p not in PERMISSION_OPTIONS for p in permissions):
        raise DomainError('Choose permissions from the supported list.')
    return name, description, status, list(dict.fromkeys(permissions))


class CreateUserProfileController(Controller):
    PERMISSION_OPTIONS = PERMISSION_OPTIONS

    def userProfileExists(self, profileName):
        self.require('profile.create')
        return UserProfile.userProfileExists(profileName)

    def createUserProfile(self, profileName, description, status, permissions):
        self.require('profile.create')
        values = validate_profile(profileName, description, status, permissions)
        if UserProfile.userProfileExists(values[0]):
            raise DomainError('A profile with this name already exists.')
        if not UserProfile.createUserProfile(*values):
            raise DomainError('A profile with this name already exists.')
        return True


class ViewUserProfileController(Controller):
    def getUserProfile(self, profileId):
        self.require('profile.view')
        profile = UserProfile.getUserProfile(profileId)
        if profile is None:
            raise NotFoundError('User profile not found.')
        return profile

    def listUserProfiles(self):
        self.require('profile.view')
        return UserProfile.listUserProfiles()


class UpdateUserProfileController(Controller):
    def getUserProfile(self, profileId):
        self.require('profile.update')
        profile = UserProfile.getUserProfile(profileId)
        if profile is None:
            raise NotFoundError('User profile not found.')
        return profile

    def updateUserProfile(self, profileId, profileName, description, permissions, status=None):
        current = self.getUserProfile(profileId)
        values = validate_profile(profileName, description, status or current.status, permissions)
        if not UserProfile.updateUserProfile(profileId, values[0], values[1], values[3], values[2]):
            raise DomainError('A profile with this name already exists.')
        return True


class SuspendUserProfileController(Controller):
    def getUserProfile(self, profileId):
        self.require('profile.suspend')
        profile = UserProfile.getUserProfile(profileId)
        if profile is None:
            raise NotFoundError('User profile not found.')
        return profile

    def suspendUserProfile(self, profileId):
        self.getUserProfile(profileId)
        return UserProfile.suspendUserProfile(profileId)


class SearchUserProfileController(Controller):
    def searchUserProfiles(self, keyword):
        self.require('profile.search')
        query = required(keyword, 'Search text', 200)
        return UserProfile.searchUserProfiles(query)

    def listUserProfiles(self):
        self.require('profile.search')
        return UserProfile.listUserProfiles()


class ProfileDirectoryController(Controller):
    def listForAction(self, mode='view'):
        permission = {'view': 'profile.view', 'update': 'profile.update', 'suspend': 'profile.suspend'}.get(mode)
        if permission is None:
            raise DomainError('Choose a supported profile operation.')
        self.require(permission)
        return UserProfile.listUserProfiles()
