from entity.projects.interior_design_project import InteriorDesignProject


class CreatePastProjectController:
    def __init__(self):
        self.entity = InteriorDesignProject()

    def createPastProject(self, accountId: str, projectName: str, categoryId: int,
                         propertyType: str, area: str, renovationCost: float, description: str) -> bool:
        return self.entity.createPastProject(accountId, projectName, categoryId, propertyType, area, renovationCost, description)
