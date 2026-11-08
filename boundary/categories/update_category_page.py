from boundary.validation import strip_input
from flask import flash, redirect, url_for
from flask.views import MethodView
from boundary.designer.context import request_values
from boundary.designer.presentation import wants_html
from boundary.portal import present, error_response
from control.categories.update_category_controller import UpdateCategoryController


class UpdateCategoryPage(MethodView):
    def get(self, category_id):
        category = UpdateCategoryController().getCategory(category_id)
        if category is None:
            return error_response('Category not found.','manager',status=404)
        return present(dict(ok=True,editing=True,category=category.as_dict(),values=category.as_dict()),
            'categories/form.html','Update Interior Design Project Category','manager')

    def post(self, category_id):
        values = request_values()
        self.onUpdate(category_id, values.get('categoryName',''),values.get('description',''))
        return self.rendered_page

    def onUpdate(self, categoryId: int, categoryName: str, description: str) -> None:
        self.values = dict(categoryName=strip_input(categoryName), description=strip_input(description))
        self.categoryId = categoryId
        controller = UpdateCategoryController()
        if controller.updateCategory(categoryId, **self.values):
            self.category = controller.getCategory(categoryId)
            self.displaySuccess()
        else:
            self.error_message, self.field_errors = controller.entity.error_message, controller.entity.field_errors
            self.error_reason = controller.entity.error_reason
            self.displayError()

    def displaySuccess(self) -> None:
        message = 'Category updated successfully.'
        if wants_html():
            flash(message,'success')
            self.rendered_page = redirect(url_for('view_category',category_id=self.category.category_id),code=303)
        else:
            self.rendered_page = dict(ok=True,message=message,category=self.category.as_dict()), 200

    def displayError(self) -> None:
        self.rendered_page = error_response(self.error_message,'manager',self.field_errors,
            status=404 if self.error_reason == 'not_found' else 400, values=self.values,
            template='portal/error.html' if self.error_reason == 'not_found' else 'categories/form.html',
            editing=True,categoryId=getattr(self,'categoryId',None))
