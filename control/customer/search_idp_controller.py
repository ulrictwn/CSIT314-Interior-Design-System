# entity/projects/interior_design_project.py: saved project data.
from entity.projects.interior_design_project import InteriorDesignProject


class SearchIDPController:
    def search_all_IDPs(self, keyword: str) -> list[InteriorDesignProject]:
        """Pass the request to InteriorDesignProject.search_all_IDPs and return its result."""
        return InteriorDesignProject.search_all_IDPs(keyword)
