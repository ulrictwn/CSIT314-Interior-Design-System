from flask import request
from flask.views import MethodView
from boundary.designer.presentation import present
from boundary.validation import search_text
from boundary.projects.validation import project_values
from boundary.designer.context import account_id, request_values
from boundary.designer.responses import error_response
from control.projects.search_new_project_controller import SearchNewProjectController
from entity.projects.interior_design_project import InteriorDesignProject
from infrastructure.errors import DomainError


class SearchNewProjectPage(MethodView):
    def __init__(self, accountId=None):
        self.accountId = accountId

    def get(self):
        self.onSearch(request.args.get('q', request.args.get('projectName', '')))
        return self.rendered_page

    def post(self):
        values = request_values()
        self.onSearch(values.get('projectName', values.get('q', '')))
        return self.rendered_page

    def onSearch(self, projectName: str) -> None:
        self.projectName = projectName
        try:
            projectName = search_text(projectName)
            accountId = account_id(self.accountId)
        except DomainError as error:
            self.rendered_page = error_response(str(error))
            return
        projects = SearchNewProjectController().searchNewProjects(accountId, projectName)
        self.displayResults(projects)

    def displayResults(self, projects: list[InteriorDesignProject]) -> None:
        self.rendered_page = present(dict(ok=True, query=self.projectName, projects=[project_values(p) for p in projects]), 200)
