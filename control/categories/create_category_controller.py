from entity.categories.category import Category


class CreateCategoryController:
    def __init__(self):
        self.entity = Category()

    def createCategory(self, categoryName: str, description: str) -> bool:
        return self.entity.createCategory(categoryName, description)
