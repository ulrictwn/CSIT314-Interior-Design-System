from entity.projects.interior_design_project import InteriorDesignProject


class UpdateNewProjectController:
    def updateNewProject(self, projectId: int, projectName: str, categoryId: int,
                         propertyType: str, area: str, renovationCost: float, description: str) -> bool:
        project = InteriorDesignProject()
        result = project.updateNewProject(projectId, projectName, categoryId, propertyType, area, renovationCost, description)
        self.error_message, self.field_errors = project.error_message, project.field_errors
        self.error_reason = project.error_reason
        return result

    def getNewProject(self, projectId: int) -> InteriorDesignProject | None:
        return InteriorDesignProject.getNewProject(projectId)
