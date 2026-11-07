from entity.shortlist.shortlist import Shortlist
from entity.projects.interior_design_project import InteriorDesignProject


class ViewShortlistCountController:
    def getShortlistCount(self, projectId: int) -> int:
        return Shortlist.getShortlistCount(projectId)

    def getProject(self, projectId):
        return InteriorDesignProject.getProject(projectId)
