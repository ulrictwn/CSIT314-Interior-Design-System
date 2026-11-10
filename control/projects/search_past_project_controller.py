# entity/projects/interior_design_project.py: project records and database operations.
from entity.projects.interior_design_project import InteriorDesignProject


class SearchPastProjectController:
    def searchPastProjects(self, accountId: str, projectName: str) -> list[InteriorDesignProject]:
        """Relay this request to the imported InteriorDesignProject entity and return its result."""
        return InteriorDesignProject.searchPastProjects(accountId, projectName)
