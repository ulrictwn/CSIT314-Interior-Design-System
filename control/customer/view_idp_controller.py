from entity.projects.interior_design_project import InteriorDesignProject


class ViewIDPController:
    def getIDP(self, projectId: int) -> InteriorDesignProject | None:
        return InteriorDesignProject.getIDP(projectId)
