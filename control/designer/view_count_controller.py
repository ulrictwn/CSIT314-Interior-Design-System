# entity/projects/interior_design_project.py: provides the saved-data entity used by this operation.
from entity.projects.interior_design_project import InteriorDesignProject


class ViewCountController:
    def getViewCount(self, projectId: int) -> int:
        """Request the saved view count from entity/projects/interior_design_project.py."""
        return InteriorDesignProject.getViewCount(projectId)
