from entity.projects.interior_design_project import InteriorDesignProject


class DeletePastProjectController:
    def deletePastProject(self, projectId: int) -> bool:
        project = InteriorDesignProject()
        result = project.deletePastProject(projectId)
        self.error_message, self.field_errors = project.error_message, project.field_errors
        self.error_reason = project.error_reason
        return result

    def getPastProject(self, projectId: int) -> InteriorDesignProject | None:
        return InteriorDesignProject.getPastProject(projectId)
