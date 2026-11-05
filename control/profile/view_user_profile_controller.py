from entity.profile.user_profile import UserProfile


class ViewUserProfileController:
    def getUserProfile(self, profileId: int) -> UserProfile | None:
        return UserProfile.getUserProfile(profileId)
