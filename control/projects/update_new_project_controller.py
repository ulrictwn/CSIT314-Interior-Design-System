from entity.projects.interior_design_project import InteriorDesignProject


class UpdateNewProjectController:
    def __init__(self):
        self.entity = InteriorDesignProject()

    def updateNewProject(self, projectId: int, projectName: str, categoryId: int,
                         propertyType: str, area: str, renovationCost: float, description: str) -> bool:
        return self.entity.updateNewProject(projectId, projectName, categoryId, propertyType, area, renovationCost, description)

    def getNewProject(self, projectId: int) -> InteriorDesignProject | None:
        return InteriorDesignProject.getNewProject(projectId)
