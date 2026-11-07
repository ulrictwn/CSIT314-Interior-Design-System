from boundary.auth.staff_login_page import StaffLoginPage
from boundary.customer.customer_login_page import CustomerLoginPage
from boundary.customer.logout_page import LogoutPage as CustomerLogoutPage
from boundary.customer.dashboard_page import CustomerDashboardPage
from boundary.customer.search_idp_page import SearchIDPPage
from boundary.customer.view_idp_page import ViewIDPPage
from boundary.customer.save_shortlist_idp_page import SaveShortlistIDPPage
from boundary.customer.search_shortlist_idp_page import SearchShortlistIDPPage
from boundary.customer.view_shortlist_idp_page import ViewShortlistIDPPage
from boundary.customer.remove_shortlist_idp_page import RemoveShortlistIDPPage
from boundary.platform_manager.platform_manager_login_page import PlatformManagerLoginPage
from boundary.platform_manager.platform_manager_logout_page import PlatformManagerLogoutPage
from boundary.platform_manager.dashboard_page import PlatformManagerDashboardPage
from boundary.categories.create_category_page import CreateCategoryPage
from boundary.categories.view_category_page import ViewCategoryPage
from boundary.categories.update_category_page import UpdateCategoryPage
from boundary.categories.delete_category_page import DeleteCategoryPage
from boundary.categories.search_category_page import SearchCategoryPage
from boundary.reports.daily_report_page import DailyReportPage
from boundary.reports.weekly_report_page import WeeklyReportPage
from boundary.reports.monthly_report_page import MonthlyReportPage
from boundary.reports.view_report_page import ViewReportPage, DownloadReportPage
from boundary.designer.view_count_page import ViewCountPage
from boundary.designer.view_shortlist_count_page import ViewShortlistCountPage
from boundary.designer.project_interest_page import ProjectInterestPage


def register_sprint_routes(app):
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
