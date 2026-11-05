from entity.projects.interior_design_project import InteriorDesignProject


class CreatePastProjectController:
    def createPastProject(self, accountId: str, projectName: str, categoryId: int,
                         propertyType: str, area: str, renovationCost: float, description: str) -> bool:
        project = InteriorDesignProject()
        result = project.createPastProject(accountId, projectName, categoryId, propertyType, area, renovationCost, description)
        self.error_message, self.field_errors = project.error_message, project.field_errors
        self.error_reason = project.error_reason
        self.project = project if result else None
        return result
