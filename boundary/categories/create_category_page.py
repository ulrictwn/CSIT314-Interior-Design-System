from flask import flash, redirect, url_for
from flask.views import MethodView
from boundary.categories.validation import validate_category_fields
from boundary.designer.context import request_values
from boundary.designer.presentation import wants_html
from boundary.projects.validation import positive_integer
from boundary.portal import present, error_response
from control.categories.create_category_controller import CreateCategoryController
from infrastructure.errors import DomainError


class CreateCategoryPage(MethodView):
    def get(self):
        return present(dict(ok=True, editing=False, values={}), 'categories/form.html','Create Interior Design Project Category','manager')

    def post(self):
        values = request_values()
        self.onCreate(values.get('categoryName',''),values.get('description',''))
        return self.rendered_page

    def onCreate(self, categoryName: str, description: str) -> None:
        self.values = dict(categoryName=categoryName,description=description)
        values, self.field_errors = validate_category_fields(categoryName,description)
        self.error_reason = 'invalid_data'
        if self.field_errors:
            self.error_message = 'Please correct the errors below.'
            self.displayError()
            return
        controller = CreateCategoryController()
        if controller.createCategory(**values):
            self.category = controller.category
            self.displaySuccess()
        else:
            self.error_message, self.field_errors, self.error_reason = controller.error_message, controller.field_errors, controller.error_reason
            self.displayError()

    def displaySuccess(self) -> None:
        message = 'Category created successfully.'
        if wants_html():
            flash(message,'success')
            self.rendered_page = redirect(url_for('view_category',category_id=self.category.category_id),code=303)
        else:
            self.rendered_page = dict(ok=True,message=message,category=self.category.as_dict()), 201

    def displayError(self) -> None:
        self.rendered_page = error_response(self.error_message,'manager',self.field_errors,
            status=404 if self.error_reason == 'not_found' else 400, values=self.values,
            template='portal/error.html' if self.error_reason == 'not_found' else 'categories/form.html',
            editing=False,categoryId=getattr(self,'categoryId',None))
