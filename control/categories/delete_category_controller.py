# entity/categories/category.py: saved IDP category data.
from entity.categories.category import Category


class DeleteCategoryController:
    def __init__(self):
        """Create the Category operation entity used by this controller."""
        self.entity = Category()

    def deleteCategory(self, categoryId: int) -> bool:
        """Pass the request to Category.deleteCategory and return its result."""
        return self.entity.deleteCategory(categoryId)
