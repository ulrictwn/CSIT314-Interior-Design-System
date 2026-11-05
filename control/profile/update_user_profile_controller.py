from entity.profile.user_profile import UserProfile


class UpdateUserProfileController:
    def getUserProfile(self, profileId: int) -> UserProfile | None:
        return UserProfile.getUserProfile(profileId)

    def updateUserProfile(self, profileId: int, profileName: str, description: str,
                          permissions: list[str]) -> bool:
        profile = UserProfile()
        updated = profile.updateUserProfile(profileId, profileName, description, permissions)
        self.error_message = profile.error_message
        self.field_errors = profile.field_errors
        self.error_reason = profile.error_reason
        return updated
