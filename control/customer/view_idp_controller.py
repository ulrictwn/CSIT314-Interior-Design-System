# entity/projects/interior_design_project.py: saved project data.
from entity.projects.interior_design_project import InteriorDesignProject


class ViewIDPController:
    def getIDP(self, projectId: int) -> InteriorDesignProject | None:
        """Pass the request to InteriorDesignProject.getIDP and return its result."""
        return InteriorDesignProject.getIDP(projectId)
