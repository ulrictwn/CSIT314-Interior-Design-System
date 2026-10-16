from entity.user_profile import UserProfile


class CreateUserProfileController:

    PERMISSION_OPTIONS = {
        "profile.create": "Create User Profiles",
        "profile.view": "View User Profiles",
        "profile.update": "Update User Profiles",
        "profile.suspend": "Suspend User Profiles",
        "profile.search": "Search User Profiles"
    }

    def userProfileExists(self, profileName: str) -> bool:
        return UserProfile.userProfileExists(profileName)

    def createUserProfile(
        self,
        profileName: str,
        description: str,
        status: str,
        permissions: list[str]
    ) -> bool:
        if not isinstance(profileName, str):
            return False

        if not isinstance(description, str):
            return False

        profileName = profileName.strip()
        description = description.strip()

        if not profileName or not description:
            return False

        if len(profileName) > 100:
            return False

        if status not in ("Active", "Suspended"):
            return False

        if not isinstance(permissions, list):
            return False

        for permission in permissions:
            if not isinstance(permission, str):
                return False

            if permission not in self.PERMISSION_OPTIONS:
                return False

        if self.userProfileExists(profileName):
            return False

        return UserProfile.createUserProfile(
            profileName,
            description,
            status,
            permissions
        )