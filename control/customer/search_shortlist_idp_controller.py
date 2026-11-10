# entity/projects/interior_design_project.py: saved project data.
from entity.projects.interior_design_project import InteriorDesignProject


class SearchShortlistIDPController:
    def search_shortlist_IDP(self, accountId: str, keyword: str) -> list[InteriorDesignProject]:
        """Pass the request to InteriorDesignProject.search_shortlist_IDP and return its result."""
        return InteriorDesignProject.search_shortlist_IDP(accountId, keyword)
