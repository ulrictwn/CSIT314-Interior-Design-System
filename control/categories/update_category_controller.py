# entity/categories/category.py: saved IDP category data.
from entity.categories.category import Category


class UpdateCategoryController:
    def __init__(self):
        """Create the Category operation entity used by this controller."""
        self.entity = Category()

    def updateCategory(self, categoryId: int, categoryName: str, description: str) -> bool:
        """Pass the request to Category.updateCategory and return its result."""
        return self.entity.updateCategory(categoryId, categoryName, description)
