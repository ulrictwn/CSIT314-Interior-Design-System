from entity.projects.interior_design_project import InteriorDesignProject


class ViewPastProjectController:

    def getPastProject(self, projectId: int) -> InteriorDesignProject | None:
        return InteriorDesignProject.getPastProject(projectId)
