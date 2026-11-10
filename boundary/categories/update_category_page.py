# control/categories/view_category_controller.py: the boundary-to-entity request handler.
from control.categories.view_category_controller import ViewCategoryController
# boundary/validation.py: ordinary text cleanup only.
from boundary.validation import strip_input
# infrastructure/errors.py: saved-data and validation errors.
from infrastructure.errors import DomainError
from flask import flash, redirect, url_for
from flask.views import MethodView
# boundary/designer/context.py: submitted values and signed-in account context.
from boundary.designer.context import request_values
# boundary/designer/presentation.py: HTML or JSON presentation choice.
from boundary.designer.presentation import wants_html
# boundary/portal.py: shared portal rendering and error displays.
from boundary.portal import present, error_response
# control/categories/update_category_controller.py: the boundary-to-entity request handler.
from control.categories.update_category_controller import UpdateCategoryController


class UpdateCategoryPage(MethodView):
    def get(self, category_id):
        """Load the existing category through ViewCategoryController for editing."""
        try:
            category = ViewCategoryController().getCategory(strip_input(category_id))
        except DomainError as error:
            return error_response(str(error), 'manager', {'categoryId': [str(error)]})
        if category is None:
            return error_response('Category not found.','manager',status=404)
        return present(dict(ok=True,editing=True,category=category.as_dict(),values=category.as_dict()),
            'categories/form.html','Update Interior Design Project Category','manager')

    def post(self, category_id):
        """Read the submitted request, run onUpdate, and return the prepared response."""
        values = request_values()
        self.onUpdate(category_id, values.get('categoryName',''),values.get('description',''))
        return self.rendered_page

    def onUpdate(self, categoryId: int, categoryName: str, description: str) -> None:
        """Strip category details and let the entity validate them through the controller."""
        self.values = dict(categoryName=strip_input(categoryName), description=strip_input(description))
        self.categoryId = strip_input(categoryId)
        controller = UpdateCategoryController()
        if controller.updateCategory(self.categoryId, **self.values):
            self.category = ViewCategoryController().getCategory(self.categoryId)
            self.displaySuccess()
        else:
            self.error_message, self.field_errors = controller.entity.error_message, controller.entity.field_errors
            self.error_reason = controller.entity.error_reason
            self.displayError()

    def displaySuccess(self) -> None:
        """Display the successful operation result or prepare its redirect."""
        message = 'Category updated successfully.'
        if wants_html():
            flash(message,'success')
            self.rendered_page = redirect(url_for('view_category',category_id=self.category.category_id),code=303)
        else:
            self.rendered_page = dict(ok=True,message=message,category=self.category.as_dict()), 200

    def displayError(self) -> None:
        """Display the input or saved-data error returned by this operation."""
        self.rendered_page = error_response(self.error_message,'manager',self.field_errors,
            status=404 if self.error_reason == 'not_found' else 400, values=self.values,
            template='portal/error.html' if self.error_reason == 'not_found' else 'categories/form.html',
            editing=True,categoryId=getattr(self,'categoryId',None))
