from entity.categories.category import Category


class DeleteCategoryController:
    def __init__(self):
        self.entity = Category()

    def deleteCategory(self, categoryId: int) -> bool:
        return self.entity.deleteCategory(categoryId)

    def getCategory(self, categoryId: int) -> Category | None:
        return Category.getCategory(categoryId)
