from entity.projects.interior_design_project import InteriorDesignProject


class ViewShortlistIDPController:
    def __init__(self, accountId=None):
        self.accountId = accountId

    def getIDP(self, projectId: int) -> InteriorDesignProject | None:
        return InteriorDesignProject.getShortlistedIDP(self.accountId, projectId)
