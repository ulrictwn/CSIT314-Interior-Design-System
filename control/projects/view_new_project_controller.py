from entity.projects.interior_design_project import InteriorDesignProject


class ViewNewProjectController:

    def getNewProject(self, projectId: int) -> InteriorDesignProject | None:
        return InteriorDesignProject.getNewProject(projectId)
