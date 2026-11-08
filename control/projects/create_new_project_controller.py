from entity.projects.interior_design_project import InteriorDesignProject


class CreateNewProjectController:
    def __init__(self):
        self.entity = InteriorDesignProject()

    def createNewProject(self, accountId: str, projectName: str, categoryId: int,
                         propertyType: str, area: str, renovationCost: float, description: str) -> bool:
        return self.entity.createNewProject(accountId, projectName, categoryId, propertyType, area, renovationCost, description)
