from entity.categories.category import Category


class UpdateCategoryController:
    def updateCategory(self, categoryId: int, categoryName: str, description: str) -> bool:
        entity = Category()
        result = entity.updateCategory(categoryId, categoryName, description)
        self.error_message, self.field_errors, self.error_reason = entity.error_message, entity.field_errors, entity.error_reason
        self.category = Category.getCategory(categoryId) if result else None
        return result

    def getCategory(self, categoryId: int) -> Category | None:
        return Category.getCategory(categoryId)
