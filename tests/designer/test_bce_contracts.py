"""Contracts transcribed from the BCE images in CSIT314 Group Project Report (3).docx."""
import importlib
import inspect
import pytest

CONTRACTS = [(13, 'company', 'CreateCompanyProfilePage', 'onCreate', ['companyName', 'companyContact', 'companyAddress', 'companyEmail', 'companyRegistrationNumber'], 'CreateCompanyProfileController', 'createCompanyProfile', ['accountId', 'companyName', 'companyContact', 'companyAddress', 'companyEmail', 'companyRegistrationNumber'], 'CompanyProfile'), (14, 'company', 'ViewCompanyProfilePage', 'onView', [], 'ViewCompanyProfileController', 'getCompanyProfile', ['accountId'], 'CompanyProfile'), (15, 'company', 'DeleteCompanyProfilePage', 'onDelete', [], 'DeleteCompanyProfileController', 'deleteCompanyProfile', ['accountId'], 'CompanyProfile'), (16, 'company', 'UpdateCompanyProfilePage', 'onUpdate', ['companyName', 'companyContact', 'companyAddress', 'companyEmail', 'companyRegistrationNumber'], 'UpdateCompanyProfileController', 'updateCompanyProfile', ['accountId', 'companyName', 'companyContact', 'companyAddress', 'companyEmail', 'companyRegistrationNumber'], 'CompanyProfile'), (17, 'company', 'SearchCompanyProfilePage', 'onSearch', ['keyword'], 'SearchCompanyProfileController', 'searchCompanyProfile', ['accountId', 'keyword'], 'CompanyProfile'), (18, 'designer', 'InteriorDesignerLoginPage', 'onLogin', ['username', 'password'], 'InteriorDesignerLoginController', 'login', ['username', 'password'], 'UserAccount'), (19, 'designer', 'InteriorDesignerLogoutPage', 'logout', [], None, None, None, None), (20, 'projects', 'CreateNewProjectPage', 'onCreate', ['projectName', 'categoryId', 'propertyType', 'area', 'renovationCost', 'description'], 'CreateNewProjectController', 'createNewProject', ['accountId', 'projectName', 'categoryId', 'propertyType', 'area', 'renovationCost', 'description'], 'InteriorDesignProject'), (21, 'projects', 'UpdateNewProjectPage', 'onUpdate', ['projectId', 'projectName', 'categoryId', 'propertyType', 'area', 'renovationCost', 'description'], 'UpdateNewProjectController', 'updateNewProject', ['projectId', 'projectName', 'categoryId', 'propertyType', 'area', 'renovationCost', 'description'], 'InteriorDesignProject'), (22, 'projects', 'ViewNewProjectPage', 'onView', ['projectId'], 'ViewNewProjectController', 'getNewProject', ['projectId'], 'InteriorDesignProject'), (23, 'projects', 'SearchNewProjectPage', 'onSearch', ['projectName'], 'SearchNewProjectController', 'searchNewProjects', ['accountId', 'projectName'], 'InteriorDesignProject'), (24, 'projects', 'DeleteNewProjectPage', 'onDelete', ['projectId'], 'DeleteNewProjectController', 'deleteNewProject', ['projectId'], 'InteriorDesignProject'), (25, 'projects', 'CreatePastProjectPage', 'onCreate', ['projectName', 'categoryId', 'propertyType', 'area', 'renovationCost', 'description'], 'CreatePastProjectController', 'createPastProject', ['accountId', 'projectName', 'categoryId', 'propertyType', 'area', 'renovationCost', 'description'], 'InteriorDesignProject'), (26, 'projects', 'ViewPastProjectPage', 'onView', ['projectId'], 'ViewPastProjectController', 'getPastProject', ['projectId'], 'InteriorDesignProject'), (27, 'projects', 'UpdatePastProjectPage', 'onUpdate', ['projectId', 'projectName', 'categoryId', 'propertyType', 'area', 'renovationCost', 'description'], 'UpdatePastProjectController', 'updatePastProject', ['projectId', 'projectName', 'categoryId', 'propertyType', 'area', 'renovationCost', 'description'], 'InteriorDesignProject'), (28, 'projects', 'SearchPastProjectPage', 'onSearch', ['projectName'], 'SearchPastProjectController', 'searchPastProjects', ['accountId', 'projectName'], 'InteriorDesignProject'), (29, 'projects', 'DeletePastProjectPage', 'onDelete', ['projectId'], 'DeletePastProjectController', 'deletePastProject', ['projectId'], 'InteriorDesignProject')]


def snake(name):
    import re
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


def parameters(method):
    return [name for name in inspect.signature(method).parameters if name not in ('self', 'cls')]


@pytest.mark.parametrize('story,feature,page_name,event,event_args,control_name,operation,args,entity_name', CONTRACTS,
                         ids=[f'story{row[0]}' for row in CONTRACTS])
def test_diagram_class_names_signatures_and_void_events(story, feature, page_name, event, event_args,
                                                      control_name, operation, args, entity_name):
    page = getattr(importlib.import_module('boundary.'+feature+'.'+snake(page_name)), page_name)
    assert parameters(getattr(page, event)) == event_args
    assert inspect.signature(getattr(page, event)).return_annotation is None
    if control_name is None:
        assert parameters(page.displayLoginPage) == []
        return
    control = getattr(importlib.import_module('control.'+feature+'.'+snake(control_name)), control_name)
    assert parameters(getattr(control, operation)) == args
    modules = {'CompanyProfile': 'entity.company.company_profile',
               'InteriorDesignProject': 'entity.projects.interior_design_project',
               'UserAccount': 'entity.accounts.user_account'}
    entity = getattr(importlib.import_module(modules[entity_name]), entity_name)
    assert parameters(getattr(entity, operation)) == (args+['profileName'] if story == 18 else args)
    if operation.startswith(('create', 'update', 'delete')) or operation == 'login':
        assert inspect.signature(getattr(control, operation)).return_annotation is bool
        assert inspect.signature(getattr(entity, operation)).return_annotation is bool
