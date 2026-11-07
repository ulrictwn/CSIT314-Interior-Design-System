from entity.categories.category import Category


class SearchCategoryController:
    def searchCategories(self, keyword: str) -> list[Category]:
        return Category.searchCategories(keyword)
