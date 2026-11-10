from flask import request
from flask.views import MethodView
# boundary/designer/presentation.py: shared HTML/JSON rendering.
from boundary.designer.presentation import present
# boundary/validation.py: ordinary text cleanup only.
from boundary.validation import strip_input
# infrastructure/errors.py: application error types.
from infrastructure.errors import DomainError
# boundary/projects/presentation.py: project form fields and display values.
from boundary.projects.presentation import project_values
# boundary/designer/context.py: submitted values and the signed-in account.
from boundary.designer.context import account_id, request_values
# boundary/designer/responses.py: shared error displays.
from boundary.designer.responses import error_response
# control/projects/search_past_project_controller.py: controller used to relay this page's entity requests.
from control.projects.search_past_project_controller import SearchPastProjectController
# entity/projects/interior_design_project.py: project records and database operations.
from entity.projects.interior_design_project import InteriorDesignProject


class SearchPastProjectPage(MethodView):
    def get(self):
        """Read the search query and pass it to onSearch."""
        self.onSearch(request.args.get('q', request.args.get('projectName', '')))
        return self.rendered_page

    def post(self):
        """Read the submitted input, call onSearch, and return the prepared response."""
        values = request_values()
        self.onSearch(values.get('projectName', values.get('q', '')))
        return self.rendered_page

    def onSearch(self, projectName: str) -> None:
        """Strip search text, then request matching records or validation errors from the entity."""
        self.projectName = strip_input(projectName)
        try:
            projects = SearchPastProjectController().searchPastProjects(account_id(), self.projectName)
        except DomainError as error:
            self.rendered_page = error_response(str(error), {'projectName': [str(error)]},
                                                values={'projectName': self.projectName})
            return
        self.displayResults(projects)

    def displayResults(self, projects: list[InteriorDesignProject]) -> None:
        """Prepare the retrieved details for the imported HTML/JSON presenter."""
        self.rendered_page = present(dict(ok=True, query=self.projectName, projects=[project_values(p) for p in projects]), 200)
