from entity.projects.interior_design_project import InteriorDesignProject


class DeletePastProjectController:
    def __init__(self):
        self.entity = InteriorDesignProject()

    def deletePastProject(self, projectId: int) -> bool:
        return self.entity.deletePastProject(projectId)

    def getPastProject(self, projectId: int) -> InteriorDesignProject | None:
        return InteriorDesignProject.getPastProject(projectId)
