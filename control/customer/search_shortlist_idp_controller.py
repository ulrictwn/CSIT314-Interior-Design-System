from entity.projects.interior_design_project import InteriorDesignProject


class SearchShortlistIDPController:
    def search_shortlist_IDP(self, accountId: str, keyword: str) -> list[InteriorDesignProject]:
        return InteriorDesignProject.search_shortlist_IDP(accountId, keyword)
