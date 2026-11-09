from entity.profile.user_profile import UserProfile


class CreateUserProfileController:
    def __init__(self):
        self.entity = UserProfile()

    def createUserProfile(self, profileName: str, description: str, status: str,
                          permissions: list[str]) -> bool:
        return self.entity.createUserProfile(profileName, description, status, permissions)