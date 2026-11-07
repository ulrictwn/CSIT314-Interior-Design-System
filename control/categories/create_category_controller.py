from entity.categories.category import Category


class CreateCategoryController:
    def createCategory(self, categoryName: str, description: str) -> bool:
        entity = Category()
        result = entity.createCategory(categoryName, description)
        self.error_message, self.field_errors, self.error_reason = entity.error_message, entity.field_errors, entity.error_reason
        self.category = entity
        return result
