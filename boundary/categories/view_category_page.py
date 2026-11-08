from boundary.validation import strip_input
from flask.views import MethodView
from boundary.portal import present, error_response
from control.categories.view_category_controller import ViewCategoryController
from entity.categories.category import Category


class ViewCategoryPage(MethodView):
    def get(self,category_id):
        self.onView(category_id)
        return self.rendered_page

    def onView(self,categoryId: int) -> None:
        categoryId = strip_input(categoryId)
        category = ViewCategoryController().getCategory(categoryId)
        if category is None:
            self.rendered_page = error_response('Category not found.','manager',status=404)
            return
        self.displayCategory(category)

    def displayCategory(self,category: Category) -> None:
        self.rendered_page = present(dict(ok=True,category=category.as_dict()),
            'categories/detail.html','View Interior Design Project Category','manager')
