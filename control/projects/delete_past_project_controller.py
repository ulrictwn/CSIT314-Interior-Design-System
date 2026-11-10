# entity/projects/interior_design_project.py: project records and database operations.
from entity.projects.interior_design_project import InteriorDesignProject


class DeletePastProjectController:
    def __init__(self):
        """Keep the imported InteriorDesignProject entity for this operation."""
        self.entity = InteriorDesignProject()

    def deletePastProject(self, projectId: int) -> bool:
        """Relay this request to the imported InteriorDesignProject entity and return its result."""
        return self.entity.deletePastProject(projectId)
