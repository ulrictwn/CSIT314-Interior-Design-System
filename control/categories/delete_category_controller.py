from entity.categories.category import Category


class DeleteCategoryController:
    def deleteCategory(self, categoryId: int) -> bool:
        entity = Category()
        result = entity.deleteCategory(categoryId)
        self.error_message, self.field_errors, self.error_reason = entity.error_message, entity.field_errors, entity.error_reason
        self.category = Category.getCategory(categoryId) if result else None
        return result

    def getCategory(self, categoryId: int) -> Category | None:
        return Category.getCategory(categoryId)
