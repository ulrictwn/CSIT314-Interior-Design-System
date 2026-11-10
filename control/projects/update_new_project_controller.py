# entity/projects/interior_design_project.py: project records and database operations.
from entity.projects.interior_design_project import InteriorDesignProject


class UpdateNewProjectController:
    def __init__(self):
        """Keep the imported InteriorDesignProject entity for this operation."""
        self.entity = InteriorDesignProject()

    def updateNewProject(self, projectId: int, projectName: str, categoryId: int,
                         propertyType: str, area: str, renovationCost: float, description: str) -> bool:
        """Relay this request to the imported InteriorDesignProject entity and return its result."""
        return self.entity.updateNewProject(projectId, projectName, categoryId, propertyType, area, renovationCost, description)
