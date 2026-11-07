from entity.projects.interior_design_project import InteriorDesignProject


class SearchIDPController:
    def search_all_IDPs(self, keyword: str) -> list[InteriorDesignProject]:
        return InteriorDesignProject.search_all_IDPs(keyword)
