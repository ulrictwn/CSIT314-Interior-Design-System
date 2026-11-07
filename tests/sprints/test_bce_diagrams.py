"""Public signatures transcribed from the Word document's Sprint 4/5 images."""
from importlib import import_module
import inspect
import pytest

CONTRACTS=[
 (30,'customer.search_idp','SearchIDP','onSearch',['keyword'],'search_all_IDPs',['keyword'],'projects.interior_design_project','InteriorDesignProject'),
 (31,'customer.view_idp','ViewIDP','onView',['projectId'],'getIDP',['projectId'],'projects.interior_design_project','InteriorDesignProject'),
 (32,'customer.save_shortlist_idp','SaveShortlistIDP','onSave',['projectId'],'saveShortlist',['accountId','projectId'],'shortlist.shortlist','Shortlist'),
 (33,'customer.search_shortlist_idp','SearchShortlistIDP','onSearch',['keyword'],'search_shortlist_IDP',['accountId','keyword'],'projects.interior_design_project','InteriorDesignProject'),
 (34,'customer.view_shortlist_idp','ViewShortlistIDP','onView',['projectId'],'getIDP',['projectId'],'projects.interior_design_project','InteriorDesignProject'),
 (35,'customer.customer_login','CustomerLogin','onLogin',['username','password'],'login',['username','password'],'accounts.user_account','UserAccount'),
 (37,'designer.view_count','ViewCount','onView',['projectId'],'getViewCount',['projectId'],'projects.interior_design_project','InteriorDesignProject'),
 (38,'designer.view_shortlist_count','ViewShortlistCount','onView',['projectId'],'getShortlistCount',['projectId'],'shortlist.shortlist','Shortlist'),
 (39,'platform_manager.platform_manager_login','PlatformManagerLogin','onLogin',['username','password'],'login',['username','password'],'accounts.user_account','UserAccount'),
 (41,'categories.create_category','CreateCategory','onCreate',['categoryName','description'],'createCategory',['categoryName','description'],'categories.category','Category'),
 (42,'categories.view_category','ViewCategory','onView',['categoryId'],'getCategory',['categoryId'],'categories.category','Category'),
 (43,'categories.update_category','UpdateCategory','onUpdate',['categoryId','categoryName','description'],'updateCategory',['categoryId','categoryName','description'],'categories.category','Category'),
 (44,'categories.delete_category','DeleteCategory','onDelete',['categoryId'],'deleteCategory',['categoryId'],'categories.category','Category'),
 (45,'categories.search_category','SearchCategory','onSearch',['keyword'],'searchCategories',['keyword'],'categories.category','Category')]


def parameters(method):
    return [p for p in inspect.signature(method).parameters if p not in ('self','cls')]


@pytest.mark.parametrize('row',CONTRACTS,ids=['story'+str(row[0]) for row in CONTRACTS])
def test_names_and_signatures_match_diagrams(row):
    story,module,name,event,event_args,operation,args,entity_module,entity_name=row
    boundary=getattr(import_module('boundary.'+module+'_page'),name+'Page')
    controller=getattr(import_module('control.'+module+'_controller'),name+'Controller')
    entity=getattr(import_module('entity.'+entity_module),entity_name)
    assert parameters(getattr(boundary,event))==event_args
    assert inspect.signature(getattr(boundary,event)).return_annotation is None
    assert parameters(getattr(controller,operation))==args
    assert parameters(getattr(entity,operation))==(args+['profileName'] if operation=='login' else args)
    if operation.startswith(('create','update','delete','save')) or operation=='login':
        assert inspect.signature(getattr(controller,operation)).return_annotation is bool
        assert inspect.signature(getattr(entity,operation)).return_annotation is bool


@pytest.mark.parametrize('module,name',[('customer.logout_page','LogoutPage'),('platform_manager.platform_manager_logout_page','PlatformManagerLogoutPage')])
def test_logout_void_methods(module,name):
    cls=getattr(import_module('boundary.'+module),name)
    for method in [cls.logout,cls.displayLoginPage]:
        assert parameters(method)==[] and inspect.signature(method).return_annotation is None


def test_additional_entity_operations():
    from entity.categories.category import Category
    from entity.projects.interior_design_project import InteriorDesignProject
    assert parameters(Category.categoryExists)==['categoryName']
    assert parameters(InteriorDesignProject.incrementViewCount)==['projectId']
    assert inspect.signature(InteriorDesignProject.incrementViewCount).return_annotation is None
