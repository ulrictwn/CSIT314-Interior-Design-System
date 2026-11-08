from entity.profile.user_profile import UserProfile


class UpdateUserProfileController:
    def __init__(self):
        self.entity = UserProfile()

    def getUserProfile(self, profileId: int) -> UserProfile | None:
        return UserProfile.getUserProfile(profileId)

    def updateUserProfile(self, profileId: int, profileName: str, description: str,
                          permissions: list[str]) -> bool:
        return self.entity.updateUserProfile(profileId, profileName, description, permissions)
