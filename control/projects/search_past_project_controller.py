from entity.projects.interior_design_project import InteriorDesignProject


class SearchPastProjectController:
    def searchPastProjects(self, accountId: str, projectName: str) -> list[InteriorDesignProject]:
        return InteriorDesignProject.searchPastProjects(accountId, projectName)
