from control.categories.view_category_controller import ViewCategoryController
from boundary.validation import strip_input
from flask import flash, redirect, url_for
from flask.views import MethodView
from boundary.designer.presentation import wants_html
from boundary.portal import present, error_response
from control.categories.delete_category_controller import DeleteCategoryController


class DeleteCategoryPage(MethodView):
    def get(self,category_id):
        category = ViewCategoryController().getCategory(category_id)
        if category is None:
            return error_response('Category not found.','manager',status=404)
        return present(dict(ok=True,category=category.as_dict(),confirmationRequired=True),
            'categories/delete.html','Delete Interior Design Project Category','manager')

    def post(self,category_id):
        self.onDelete(category_id)
        return self.rendered_page

    def onDelete(self,categoryId: int) -> None:
        categoryId = strip_input(categoryId)
        controller = DeleteCategoryController()
        if controller.deleteCategory(categoryId):
            self.displaySuccess()
        else:
            category = ViewCategoryController().getCategory(categoryId)
            self.rendered_page = error_response(controller.entity.error_message,'manager',
                status=404 if controller.entity.error_reason == 'not_found' else 400,
                template='categories/delete.html' if category else 'portal/error.html',
                category=category.as_dict() if category else None)

    def displaySuccess(self) -> None:
        message = 'Category deleted successfully.'
        if wants_html():
            flash(message,'success')
            self.rendered_page = redirect(url_for('search_categories',mode='delete'),code=303)
        else:
            self.rendered_page = dict(ok=True,message=message),200
