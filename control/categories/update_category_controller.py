from entity.categories.category import Category


class UpdateCategoryController:
    def __init__(self):
        self.entity = Category()

    def updateCategory(self, categoryId: int, categoryName: str, description: str) -> bool:
        return self.entity.updateCategory(categoryId, categoryName, description)
