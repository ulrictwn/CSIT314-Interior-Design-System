from entity.projects.interior_design_project import InteriorDesignProject


class SearchNewProjectController:
    def searchNewProjects(self, accountId: str, projectName: str) -> list[InteriorDesignProject]:
        return InteriorDesignProject.searchNewProjects(accountId, projectName)
