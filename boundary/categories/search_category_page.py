from flask import request
from flask.views import MethodView
# boundary/validation.py: input cleanup and field checks.
from boundary.validation import strip_input, search_text
# infrastructure/errors.py: saved-data and validation errors.
from infrastructure.errors import DomainError
# boundary/designer/context.py: submitted values and signed-in account context.
from boundary.designer.context import request_values
# boundary/portal.py: shared portal rendering and error displays.
from boundary.portal import present, error_response
# control/categories/search_category_controller.py: the boundary-to-entity request handler.
from control.categories.search_category_controller import SearchCategoryController
# entity/categories/category.py: saved IDP category data.
from entity.categories.category import Category


class SearchCategoryPage(MethodView):
    def get(self):
        """Display categories matching the supplied search keyword."""
        self.mode = request.args.get('mode','search')
        if self.mode not in ('search','view','update','delete'):
            return error_response('Choose a supported category operation.','manager')
        self.onSearch(request.args.get('q',''))
        return self.rendered_page

    def post(self):
        """Read the submitted request, run onSearch, and return the prepared response."""
        self.mode = 'search'
        self.onSearch(request_values().get('keyword',request_values().get('q','')))
        return self.rendered_page

    def onSearch(self,keyword: str) -> None:
        """Validate the keyword, then request matching records through the search controller."""
        try:
            self.keyword = search_text(strip_input(keyword))
        except DomainError as error:
            self.rendered_page = error_response(str(error), 'manager', {'keyword': [str(error)]})
            return
        self.displayResults(SearchCategoryController().searchCategories(self.keyword))

    def displayResults(self,categories: list[Category]) -> None:
        """Display the returned records using the shared portal presenter."""
        mode = getattr(self,'mode','search')
        self.rendered_page = present(dict(ok=True,categories=[c.as_dict() for c in categories],query=self.keyword,mode=mode),
            'categories/index.html',mode.title()+' Interior Design Project Categories','manager')
