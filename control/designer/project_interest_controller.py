# entity/projects/interior_design_project.py: provides the saved-data entity used by this operation.
from entity.projects.interior_design_project import InteriorDesignProject


class ProjectInterestController:
    def projects(self, accountId):
        """Request project-interest totals from entity/projects/interior_design_project.py."""
        return InteriorDesignProject.projectInterest(accountId)

    def getProject(self, projectId):
        """Request project display details from entity/projects/interior_design_project.py."""
        return InteriorDesignProject.getProject(projectId)
