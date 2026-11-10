# boundary/validation.py: ordinary text cleanup only.
from boundary.validation import strip_input
# infrastructure/errors.py: saved-data and validation errors.
from infrastructure.errors import DomainError
from flask.views import MethodView
# boundary/portal.py: shared portal rendering and error displays.
from boundary.portal import present, error_response
# control/categories/view_category_controller.py: the boundary-to-entity request handler.
from control.categories.view_category_controller import ViewCategoryController
# entity/categories/category.py: saved IDP category data.
from entity.categories.category import Category


class ViewCategoryPage(MethodView):
    def get(self,category_id):
        """Receive the category URL and run the diagram onView event."""
        self.onView(category_id)
        return self.rendered_page

    def onView(self,categoryId: int) -> None:
        """Strip the supplied ID and display saved details or the entity validation error."""
        try:
            category = ViewCategoryController().getCategory(strip_input(categoryId))
        except DomainError as error:
            self.rendered_page = error_response(str(error), 'manager', {'categoryId': [str(error)]})
            return
        if category is None:
            self.rendered_page = error_response('Category not found.','manager',status=404)
            return
        self.displayCategory(category)

    def displayCategory(self,category: Category) -> None:
        """Display the category details and its saved project count."""
        self.rendered_page = present(dict(ok=True,category=category.as_dict()),
            'categories/detail.html','View Interior Design Project Category','manager')
