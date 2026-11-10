# entity/categories/category.py: saved IDP category data.
from entity.categories.category import Category


class CreateCategoryController:
    def __init__(self):
        """Create the Category operation entity used by this controller."""
        self.entity = Category()

    def createCategory(self, categoryName: str, description: str) -> bool:
        """Pass the request to Category.createCategory and return its result."""
        return self.entity.createCategory(categoryName, description)
