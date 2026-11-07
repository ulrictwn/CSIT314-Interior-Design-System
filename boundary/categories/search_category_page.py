from flask import request
from flask.views import MethodView
from boundary.validation import search_text
from boundary.designer.context import request_values
from boundary.portal import present, error_response
from control.categories.search_category_controller import SearchCategoryController
from entity.categories.category import Category
from infrastructure.errors import DomainError


class SearchCategoryPage(MethodView):
    def get(self):
        self.mode = request.args.get('mode','search')
        if self.mode not in ('search','view','update','delete'):
            return error_response('Choose a supported category operation.','manager')
        self.onSearch(request.args.get('q',''))
        return self.rendered_page

    def post(self):
        self.mode = 'search'
        self.onSearch(request_values().get('keyword',request_values().get('q','')))
        return self.rendered_page

    def onSearch(self,keyword: str) -> None:
        try:
            self.keyword = search_text(keyword)
        except DomainError as error:
            self.rendered_page = error_response(str(error),'manager',{'keyword':[str(error)]})
            return
        self.displayResults(SearchCategoryController().searchCategories(self.keyword))

    def displayResults(self,categories: list[Category]) -> None:
        mode = getattr(self,'mode','search')
        self.rendered_page = present(dict(ok=True,categories=[c.as_dict() for c in categories],query=self.keyword,mode=mode),
            'categories/index.html',mode.title()+' Interior Design Project Categories','manager')
