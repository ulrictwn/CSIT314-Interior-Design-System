from entity.projects.interior_design_project import InteriorDesignProject


class ProjectInterestController:
    def projects(self, accountId):
        return InteriorDesignProject.projectInterest(accountId)

    def getProject(self, projectId):
        return InteriorDesignProject.getProject(projectId)
