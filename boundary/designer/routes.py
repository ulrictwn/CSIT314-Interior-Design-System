from boundary.company.create_company_profile_page import CreateCompanyProfilePage
from boundary.company.view_company_profile_page import ViewCompanyProfilePage
from boundary.company.delete_company_profile_page import DeleteCompanyProfilePage
from boundary.company.update_company_profile_page import UpdateCompanyProfilePage
from boundary.company.search_company_profile_page import SearchCompanyProfilePage
from boundary.designer.interior_designer_login_page import InteriorDesignerLoginPage
from boundary.designer.interior_designer_logout_page import InteriorDesignerLogoutPage
from boundary.designer.dashboard_page import InteriorDesignerDashboardPage
from boundary.projects.create_new_project_page import CreateNewProjectPage
from boundary.projects.update_new_project_page import UpdateNewProjectPage
from boundary.projects.view_new_project_page import ViewNewProjectPage
from boundary.projects.search_new_project_page import SearchNewProjectPage
from boundary.projects.delete_new_project_page import DeleteNewProjectPage
from boundary.projects.create_past_project_page import CreatePastProjectPage
from boundary.projects.update_past_project_page import UpdatePastProjectPage
from boundary.projects.view_past_project_page import ViewPastProjectPage
from boundary.projects.search_past_project_page import SearchPastProjectPage
from boundary.projects.delete_past_project_page import DeletePastProjectPage


def register_designer_routes(app):
    routes = [
        ('/designer', 'designer_dashboard', InteriorDesignerDashboardPage),
        ('/designer/login', 'interior_designer_login', InteriorDesignerLoginPage),
        ('/designer/logout', 'interior_designer_logout', InteriorDesignerLogoutPage),
        ('/designer/company/create', 'create_company_profile', CreateCompanyProfilePage),
        ('/designer/company', 'view_company_profile', ViewCompanyProfilePage),
        ('/designer/company/delete', 'delete_company_profile', DeleteCompanyProfilePage),
        ('/designer/company/update', 'update_company_profile', UpdateCompanyProfilePage),
        ('/designer/company/search', 'search_company_profile', SearchCompanyProfilePage),
        ('/designer/projects/new', 'new_projects', SearchNewProjectPage),
        ('/designer/projects/new/create', 'create_new_project', CreateNewProjectPage),
        ('/designer/projects/new/search', 'search_new_projects', SearchNewProjectPage),
        ('/designer/projects/new/<int:project_id>', 'view_new_project', ViewNewProjectPage),
        ('/designer/projects/new/<int:project_id>/update', 'update_new_project', UpdateNewProjectPage),
        ('/designer/projects/new/<int:project_id>/delete', 'delete_new_project', DeleteNewProjectPage),
        ('/designer/projects/past', 'past_projects', SearchPastProjectPage),
        ('/designer/projects/past/create', 'create_past_project', CreatePastProjectPage),
        ('/designer/projects/past/search', 'search_past_projects', SearchPastProjectPage),
        ('/designer/projects/past/<int:project_id>', 'view_past_project', ViewPastProjectPage),
        ('/designer/projects/past/<int:project_id>/update', 'update_past_project', UpdatePastProjectPage),
        ('/designer/projects/past/<int:project_id>/delete', 'delete_past_project', DeletePastProjectPage),
    ]
    for path, name, page in routes:
        app.add_url_rule(path, view_func=page.as_view(name))
