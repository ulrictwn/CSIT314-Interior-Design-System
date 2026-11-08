from entity.projects.interior_design_project import InteriorDesignProject


class DeleteNewProjectController:
    def __init__(self):
        self.entity = InteriorDesignProject()

    def deleteNewProject(self, projectId: int) -> bool:
        return self.entity.deleteNewProject(projectId)

    def getNewProject(self, projectId: int) -> InteriorDesignProject | None:
        return InteriorDesignProject.getNewProject(projectId)
