# entity/projects/interior_design_project.py: project records and database operations.
from entity.projects.interior_design_project import InteriorDesignProject


class ViewNewProjectController:

    def getNewProject(self, projectId: int) -> InteriorDesignProject | None:
        """Relay this request to the imported InteriorDesignProject entity and return its result."""
        return InteriorDesignProject.getNewProject(projectId)
