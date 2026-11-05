from entity.projects.interior_design_project import InteriorDesignProject


class DeleteNewProjectController:
    def deleteNewProject(self, projectId: int) -> bool:
        project = InteriorDesignProject()
        result = project.deleteNewProject(projectId)
        self.error_message, self.field_errors = project.error_message, project.field_errors
        self.error_reason = project.error_reason
        return result

    def getNewProject(self, projectId: int) -> InteriorDesignProject | None:
        return InteriorDesignProject.getNewProject(projectId)
