# entity/projects/interior_design_project.py: project records and database operations.
from entity.projects.interior_design_project import InteriorDesignProject


class CreateNewProjectController:
    def __init__(self):
        """Keep the imported InteriorDesignProject entity for this operation."""
        self.entity = InteriorDesignProject()

    def createNewProject(self, accountId: str, projectName: str, categoryId: int,
                         propertyType: str, area: str, renovationCost: float, description: str) -> bool:
        """Relay this request to the imported InteriorDesignProject entity and return its result."""
        return self.entity.createNewProject(accountId, projectName, categoryId, propertyType, area, renovationCost, description)
