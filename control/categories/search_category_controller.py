# entity/categories/category.py: saved IDP category data.
from entity.categories.category import Category


class SearchCategoryController:
    def searchCategories(self, keyword: str) -> list[Category]:
        """Pass the request to Category.searchCategories and return its result."""
        return Category.searchCategories(keyword)
