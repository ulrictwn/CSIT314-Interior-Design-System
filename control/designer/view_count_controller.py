from entity.projects.interior_design_project import InteriorDesignProject


class ViewCountController:
    def getViewCount(self, projectId: int) -> int:
        return InteriorDesignProject.getViewCount(projectId)

    def getProject(self, projectId):
        return InteriorDesignProject.getProject(projectId)
