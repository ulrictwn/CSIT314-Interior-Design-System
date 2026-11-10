# boundary/auth/staff_login_page.py: provides the boundary classes used by these routes.
from boundary.auth.staff_login_page import StaffLoginPage
# boundary/customer/customer_login_page.py: provides the boundary classes used by these routes.
from boundary.customer.customer_login_page import CustomerLoginPage
# boundary/customer/logout_page.py: provides the boundary classes used by these routes.
from boundary.customer.logout_page import LogoutPage as CustomerLogoutPage
# boundary/customer/dashboard_page.py: provides the boundary classes used by these routes.
from boundary.customer.dashboard_page import CustomerDashboardPage
# boundary/customer/search_idp_page.py: provides the boundary classes used by these routes.
from boundary.customer.search_idp_page import SearchIDPPage
# boundary/customer/view_idp_page.py: provides the boundary classes used by these routes.
from boundary.customer.view_idp_page import ViewIDPPage
# boundary/customer/save_shortlist_idp_page.py: provides the boundary classes used by these routes.
from boundary.customer.save_shortlist_idp_page import SaveShortlistIDPPage
# boundary/customer/search_shortlist_idp_page.py: provides the boundary classes used by these routes.
from boundary.customer.search_shortlist_idp_page import SearchShortlistIDPPage
# boundary/customer/view_shortlist_idp_page.py: provides the boundary classes used by these routes.
from boundary.customer.view_shortlist_idp_page import ViewShortlistIDPPage
# boundary/customer/remove_shortlist_idp_page.py: provides the boundary classes used by these routes.
from boundary.customer.remove_shortlist_idp_page import RemoveShortlistIDPPage
# boundary/platform_manager/platform_manager_login_page.py: provides the boundary classes used by these routes.
from boundary.platform_manager.platform_manager_login_page import PlatformManagerLoginPage
# boundary/platform_manager/platform_manager_logout_page.py: provides the boundary classes used by these routes.
from boundary.platform_manager.platform_manager_logout_page import PlatformManagerLogoutPage
# boundary/platform_manager/dashboard_page.py: provides the boundary classes used by these routes.
from boundary.platform_manager.dashboard_page import PlatformManagerDashboardPage
# boundary/categories/create_category_page.py: provides the boundary classes used by these routes.
from boundary.categories.create_category_page import CreateCategoryPage
# boundary/categories/view_category_page.py: provides the boundary classes used by these routes.
from boundary.categories.view_category_page import ViewCategoryPage
# boundary/categories/update_category_page.py: provides the boundary classes used by these routes.
from boundary.categories.update_category_page import UpdateCategoryPage
# boundary/categories/delete_category_page.py: provides the boundary classes used by these routes.
from boundary.categories.delete_category_page import DeleteCategoryPage
# boundary/categories/search_category_page.py: provides the boundary classes used by these routes.
from boundary.categories.search_category_page import SearchCategoryPage
# boundary/reports/daily_report_page.py: provides the boundary classes used by these routes.
from boundary.reports.daily_report_page import DailyReportPage
# boundary/reports/weekly_report_page.py: provides the boundary classes used by these routes.
from boundary.reports.weekly_report_page import WeeklyReportPage
# boundary/reports/monthly_report_page.py: provides the boundary classes used by these routes.
from boundary.reports.monthly_report_page import MonthlyReportPage
# boundary/reports/view_report_page.py: provides the boundary classes used by these routes.
from boundary.reports.view_report_page import ViewReportPage, DownloadReportPage
# boundary/designer/view_count_page.py: provides the boundary classes used by these routes.
from boundary.designer.view_count_page import ViewCountPage
# boundary/designer/view_shortlist_count_page.py: provides the boundary classes used by these routes.
from boundary.designer.view_shortlist_count_page import ViewShortlistCountPage
# boundary/designer/project_interest_page.py: provides the boundary classes used by these routes.
from boundary.designer.project_interest_page import ProjectInterestPage


def register_sprint_routes(app):
    """Connect customer, category, report and interest URLs to their imported boundary classes."""
    routes = [
        ('/staff/login','staff_login',StaffLoginPage),
        ('/customer/login','customer_login',CustomerLoginPage),
        ('/customer/logout','customer_logout',CustomerLogoutPage),
        ('/customer','customer_dashboard',CustomerDashboardPage),
        ('/customer/projects','customer_projects',SearchIDPPage),
        ('/customer/projects/search','search_idps',SearchIDPPage),
        ('/customer/projects/<int:project_id>','view_idp',ViewIDPPage),
        ('/customer/projects/<int:project_id>/shortlist','save_shortlist_idp',SaveShortlistIDPPage),
        ('/customer/shortlist','search_shortlist_idps',SearchShortlistIDPPage),
        ('/customer/shortlist/<int:project_id>','view_shortlist_idp',ViewShortlistIDPPage),
        ('/customer/shortlist/<int:project_id>/remove','remove_shortlist_idp',RemoveShortlistIDPPage),
        ('/manager/login','platform_manager_login',PlatformManagerLoginPage),
        ('/manager/logout','platform_manager_logout',PlatformManagerLogoutPage),
        ('/manager','platform_manager_dashboard',PlatformManagerDashboardPage),
        ('/manager/categories','categories',SearchCategoryPage),
        ('/manager/categories/search','search_categories',SearchCategoryPage),
        ('/manager/categories/create','create_category',CreateCategoryPage),
        ('/manager/categories/<int:category_id>','view_category',ViewCategoryPage),
        ('/manager/categories/<int:category_id>/update','update_category',UpdateCategoryPage),
        ('/manager/categories/<int:category_id>/delete','delete_category',DeleteCategoryPage),
        ('/manager/reports/daily','generate_daily_report',DailyReportPage),
        ('/manager/reports/weekly','generate_weekly_report',WeeklyReportPage),
        ('/manager/reports/monthly','generate_monthly_report',MonthlyReportPage),
        ('/manager/reports/<int:report_id>','view_report',ViewReportPage),
        ('/manager/reports/<int:report_id>/download','download_report',DownloadReportPage),
        ('/designer/projects/<int:project_id>/views','view_count',ViewCountPage),
        ('/designer/projects/<int:project_id>/shortlists','view_shortlist_count',ViewShortlistCountPage),
    ]
    for path,name,page in routes:
        app.add_url_rule(path,view_func=page.as_view(name))
    for metric,endpoint in [('views','project_view_counts'),('shortlists','project_shortlist_counts')]:
        app.add_url_rule('/designer/interest/'+metric,defaults={'metric':metric},
                         view_func=ProjectInterestPage.as_view(endpoint))
