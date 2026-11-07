from entity.categories.category import Category


class ViewCategoryController:
    def getCategory(self, categoryId: int) -> Category | None:
        return Category.getCategory(categoryId)
