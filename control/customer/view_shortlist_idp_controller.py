# entity/projects/interior_design_project.py: saved project data.
from entity.projects.interior_design_project import InteriorDesignProject


class ViewShortlistIDPController:
    def __init__(self, accountId=None):
        """Store the account ID used to look up this customer's saved project."""
        self.accountId = accountId

    def getIDP(self, projectId: int) -> InteriorDesignProject | None:
        """Pass the request to InteriorDesignProject.getShortlistedIDP and return its result."""
        return InteriorDesignProject.getShortlistedIDP(self.accountId, projectId)
