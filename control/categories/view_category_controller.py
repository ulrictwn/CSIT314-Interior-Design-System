# entity/categories/category.py: saved IDP category data.
from entity.categories.category import Category


class ViewCategoryController:
    def getCategory(self, categoryId: int) -> Category | None:
        """Pass the request to Category.getCategory and return its result."""
        return Category.getCategory(categoryId)
