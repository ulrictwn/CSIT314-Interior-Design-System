from unittest.mock import Mock
import pytest

from boundary.projects.create_new_project_page import CreateNewProjectPage
from boundary.projects.create_past_project_page import CreatePastProjectPage
from boundary.projects.update_new_project_page import UpdateNewProjectPage
from boundary.projects.update_past_project_page import UpdatePastProjectPage
from control.projects.create_new_project_controller import CreateNewProjectController
from control.projects.create_past_project_controller import CreatePastProjectController
from control.projects.update_new_project_controller import UpdateNewProjectController
from control.projects.update_past_project_controller import UpdatePastProjectController
from entity.accounts.user_account import UserAccount
from entity.projects.interior_design_project import InteriorDesignProject
from infrastructure.database import db


@pytest.mark.parametrize('kind', ['New', 'Past'])
def test_project_lifecycle_json_and_form_input(app, client, designer_accounts, project_data, kind):
    owner, other = designer_accounts
    base = '/designer/projects/'+kind.lower()
    raw = dict(project_data, projectName='  Seaside Home  ', propertyType=' Apartment ',
               categoryId='1', area=' 120 sqm ', renovationCost='80000.50', description=' A bright renovation project. ')
    response = client.post(base+'/create', json=dict(accountId=owner, **raw))
    assert response.status_code == 201
    project = response.json['project']
    project_id = project['projectId']
    assert project == dict(projectId=project_id, accountId=owner, status=kind, **project_data)
    assert client.get(base+f'/{project_id}').json['project'] == project
    prefill = client.get(base+f'/{project_id}/update')
    assert prefill.json['values']['projectName'] == project_data['projectName']
    changed = dict(project_data, projectName='Edited Home', categoryId=999, area='140 sqm')
    assert client.post(base+f'/{project_id}/update', data=changed).status_code == 200
    response = client.get(base+'/search', query_string={'accountId': owner, 'q': ' EDITED '})
    assert [p['projectId'] for p in response.json['projects']] == [project_id]
    assert client.get(base, query_string={'accountId': other}).json['projects'] == []
    confirmation = client.get(base+f'/{project_id}/delete')
    assert confirmation.json['confirmationRequired'] is True
    with app.app_context():
        assert getattr(InteriorDesignProject, 'get'+kind+'Project')(project_id) is not None
    assert client.post(base+f'/{project_id}/delete').status_code == 200
    assert client.get(base+f'/{project_id}').status_code == 404
    assert client.post(base+f'/{project_id}/delete').status_code == 404
    with app.app_context():
        assert UserAccount.getUserAccount(owner) is not None


@pytest.mark.parametrize('patch,field', [
    ({'projectName': ''}, 'projectName'), ({'projectName': 'x'*151}, 'projectName'),
    ({'categoryId': None}, 'categoryId'), ({'categoryId': True}, 'categoryId'),
    ({'categoryId': 0}, 'categoryId'), ({'categoryId': 1.5}, 'categoryId'),
    ({'categoryId': 'bad'}, 'categoryId'), ({'categoryId': 2_147_483_648}, 'categoryId'),
    ({'propertyType': ''}, 'propertyType'), ({'area': None}, 'area'), ({'area': 120}, 'area'),
    ({'renovationCost': ''}, 'renovationCost'), ({'renovationCost': True}, 'renovationCost'),
    ({'renovationCost': -1}, 'renovationCost'), ({'renovationCost': float('inf')}, 'renovationCost'),
    ({'renovationCost': float('nan')}, 'renovationCost'),
    ({'description': '   '}, 'description'), ({'description': 'x'*10001}, 'description'),
])
@pytest.mark.parametrize('kind,action,page_type,controller_type', [
    ('New', 'Create', CreateNewProjectPage, CreateNewProjectController),
    ('Past', 'Create', CreatePastProjectPage, CreatePastProjectController),
    ('New', 'Update', UpdateNewProjectPage, UpdateNewProjectController),
    ('Past', 'Update', UpdatePastProjectPage, UpdatePastProjectController),
])
def test_project_boundaries_reject_fields_before_controller(project_data, monkeypatch,
        patch, field, kind, action, page_type, controller_type):
    operation = Mock(side_effect=AssertionError('Invalid project input reached the controller'))
    monkeypatch.setattr(controller_type, action.lower()+kind+'Project', operation)
    page = page_type(accountId='101') if action == 'Create' else page_type()
    args = {**project_data, **patch}
    if action == 'Update':
        args['projectId'] = 1
    assert getattr(page, 'on'+action)(**args) is None
    assert page.rendered_page[1] == 400 and field in page.field_errors
    operation.assert_not_called()


@pytest.mark.parametrize('kind', ['New', 'Past'])
def test_entity_duplicate_names_and_rollback(app, designer_accounts, project_data, monkeypatch, kind):
    owner, other = designer_accounts
    create = 'create'+kind+'Project'
    update = 'update'+kind+'Project'
    get = getattr(InteriorDesignProject, 'get'+kind+'Project')
    with app.app_context():
        first = InteriorDesignProject()
        assert getattr(first, create)(owner, **project_data) is True
        project_id = first.project_id
        operation = InteriorDesignProject()
        assert getattr(operation, create)(owner, **dict(project_data, projectName='SEASIDE HOME')) is False
        assert operation.field_errors['projectName']
        # Another owner can use the same name, and New/Past have separate name spaces.
        assert getattr(InteriorDesignProject(), create)(other, **project_data) is True
        other_phase = 'Past' if kind == 'New' else 'New'
        assert getattr(InteriorDesignProject(), 'create'+other_phase+'Project')(owner, **project_data) is True
        second = InteriorDesignProject()
        assert getattr(second, create)(owner, **dict(project_data, projectName='Second Home')) is True
        assert getattr(InteriorDesignProject(), update)(project_id, **dict(project_data, projectName='second home')) is False
        assert get(project_id).project_name == 'Seaside Home'
        assert getattr(InteriorDesignProject(), update)(project_id, **project_data) is True
        monkeypatch.setattr(InteriorDesignProject, '_name_exists', lambda *args: False)
        assert getattr(InteriorDesignProject(), create)(owner, **project_data) is False
        assert getattr(InteriorDesignProject(), create)(owner, **dict(project_data, projectName='After rollback')) is True


@pytest.mark.parametrize('kind', ['New', 'Past'])
def test_operations_do_not_cross_new_and_past_types(app, designer_accounts, project_data, kind):
    owner, _ = designer_accounts
    other = 'Past' if kind == 'New' else 'New'
    with app.app_context():
        project = InteriorDesignProject()
        assert getattr(project, 'create'+kind+'Project')(owner, **project_data)
        project_id = project.project_id
        assert getattr(InteriorDesignProject, 'get'+other+'Project')(project_id) is None
        assert getattr(InteriorDesignProject(), 'update'+other+'Project')(project_id, **project_data) is False
        assert getattr(InteriorDesignProject(), 'delete'+other+'Project')(project_id) is False
        assert getattr(InteriorDesignProject, 'get'+kind+'Project')(project_id) is not None


@pytest.mark.parametrize('kind', ['New', 'Past'])
def test_project_search_filters_owner_phase_and_literal_name(app, designer_accounts, project_data, kind):
    owner, other = designer_accounts
    create = 'create'+kind+'Project'
    with app.app_context():
        for name in ['Percent%Home', 'Under_score Home', 'Ordinary Home']:
            assert getattr(InteriorDesignProject(), create)(owner, **dict(project_data, projectName=name))
        assert getattr(InteriorDesignProject(), create)(other, **project_data)
        search = getattr(InteriorDesignProject, 'search'+kind+'Projects')
        assert [p.project_name for p in search(owner, '%')] == ['Percent%Home']
        assert [p.project_name for p in search(owner, '_')] == ['Under_score Home']
        assert len(search(owner, 'home')) == 3
        assert len(search(other, '')) == 1
        assert search(owner, 'no-match') == []


def test_category_lookup_is_required_now_that_sprint_5_categories_exist(client, designer_accounts, project_data):
    owner, _ = designer_accounts
    response = client.post('/designer/projects/new/create', json=dict(accountId=owner,
        **dict(project_data, categoryId=999999)))
    assert response.status_code == 400 and response.json['errors']['categoryId']
    assert 'category' in db.metadata.tables


def test_invalid_project_edit_preserves_saved_values(app, client, designer_accounts, project_data):
    owner, _ = designer_accounts
    created = client.post('/designer/projects/past/create', json=dict(accountId=owner, **project_data))
    project_id = created.json['project']['projectId']
    response = client.post(f'/designer/projects/past/{project_id}/update', json=dict(project_data, renovationCost=-1))
    assert response.status_code == 400 and response.json['errors']['renovationCost']
    with app.app_context():
        assert InteriorDesignProject.getPastProject(project_id).renovation_cost == project_data['renovationCost']


@pytest.mark.parametrize('kind', ['New', 'Past'])
def test_unknown_owner_and_project_are_data_errors(app, designer_accounts, project_data, kind):
    with app.app_context():
        operation = InteriorDesignProject()
        assert getattr(operation, 'create'+kind+'Project')('missing', **project_data) is False
        assert operation.error_reason == 'not_found'
        assert getattr(InteriorDesignProject, 'get'+kind+'Project')(999999) is None
        assert getattr(InteriorDesignProject(), 'update'+kind+'Project')(999999, **project_data) is False
        assert getattr(InteriorDesignProject(), 'delete'+kind+'Project')(999999) is False
