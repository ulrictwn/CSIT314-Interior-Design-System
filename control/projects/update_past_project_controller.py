from entity.projects.interior_design_project import InteriorDesignProject


class UpdatePastProjectController:
    def __init__(self):
        self.entity = InteriorDesignProject()

    def updatePastProject(self, projectId: int, projectName: str, categoryId: int,
                         propertyType: str, area: str, renovationCost: float, description: str) -> bool:
        return self.entity.updatePastProject(projectId, projectName, categoryId, propertyType, area, renovationCost, description)
