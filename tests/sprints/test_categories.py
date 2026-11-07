from unittest.mock import Mock
import pytest
from sqlalchemy.exc import IntegrityError
from boundary.categories.create_category_page import CreateCategoryPage
from boundary.categories.update_category_page import UpdateCategoryPage
from control.categories.create_category_controller import CreateCategoryController
from control.categories.update_category_controller import UpdateCategoryController
from entity.categories.category import Category
from entity.projects.interior_design_project import InteriorDesignProject
from infrastructure.database import db

HTML={'Accept':'text/html'}


def test_category_lifecycle_duplicate_checks_search_prefill_and_cancel(app,client):
    data=dict(categoryName=' Japandi ',description=' Japanese simplicity meets Scandinavian warmth. ')
    response=client.post('/manager/categories/create',json=data)
    assert response.status_code==201
    category=response.json['category']; category_id=category['categoryId']
    assert category['categoryName']=='Japandi' and category['description']==data['description'].strip()
    assert client.post('/manager/categories/create',json=dict(data,categoryName='JAPANDI')).status_code==400
    assert len(client.get('/manager/categories/search?q=JAPANDI').json['categories'])==1
    assert len(client.get(f'/manager/categories/search?q=CAT{category_id}').json['categories'])==1
    assert client.get('/manager/categories/search?q=no-match').json['categories']==[]
    assert client.get(f'/manager/categories/{category_id}').json['category']['categoryName']=='Japandi'
    assert client.get(f'/manager/categories/{category_id}/update').json['values']['categoryName']=='Japandi'
    confirmation=client.get(f'/manager/categories/{category_id}/delete')
    assert confirmation.json['confirmationRequired']
    with app.app_context(): assert Category.getCategory(category_id) is not None
    assert client.post(f'/manager/categories/{category_id}/update',json=dict(categoryName='Coastal',description='Light, open spaces.')).status_code==200
    assert client.post('/manager/categories/create',json=dict(categoryName='Bohemian',description='Warm layers.')).status_code==201
    duplicate=client.post(f'/manager/categories/{category_id}/update',json=dict(categoryName='bohemian',description='Keep old name.'))
    assert duplicate.status_code==400
    assert client.get(f'/manager/categories/{category_id}').json['category']['categoryName']=='Coastal'
    assert client.post(f'/manager/categories/{category_id}/delete').status_code==200
    assert client.get(f'/manager/categories/{category_id}').status_code==404
    assert client.post(f'/manager/categories/{category_id}/delete').status_code==404


@pytest.mark.parametrize('patch,field',[({'categoryName':''},'categoryName'),({'categoryName':' '*5},'categoryName'),
    ({'categoryName':'x'*101},'categoryName'),({'categoryName':True},'categoryName'),
    ({'description':None},'description'),({'description':'x'*10001},'description')])
@pytest.mark.parametrize('page_class,controller,event,operation',[
    (CreateCategoryPage,CreateCategoryController,'onCreate','createCategory'),
    (UpdateCategoryPage,UpdateCategoryController,'onUpdate','updateCategory')])
def test_invalid_fields_stop_before_controller(monkeypatch,patch,field,page_class,controller,event,operation):
    call=Mock(side_effect=AssertionError('Invalid fields reached controller'))
    monkeypatch.setattr(controller,operation,call)
    page=page_class(); args=dict(categoryName='Japandi',description='Warm natural interiors.',**{})
    args.update(patch)
    if event=='onUpdate': args['categoryId']=1
    assert getattr(page,event)(**args) is None
    assert page.rendered_page[1]==400 and field in page.field_errors
    call.assert_not_called()


def test_in_use_category_cannot_be_deleted_and_project_category_must_exist(app,client,sprint_projects,project_data,designer_accounts):
    category_id=project_data['categoryId']
    response=client.post(f'/manager/categories/{category_id}/delete')
    assert response.status_code==400 and 'used by projects' in response.json['message']
    with app.app_context():
        assert Category.getCategory(category_id) is not None
        assert InteriorDesignProject.getProject(sprint_projects[0]) is not None
        with pytest.raises(IntegrityError):
            db.session.execute(db.delete(Category).where(Category.category_id==category_id))
            db.session.commit()
        db.session.rollback()
    response=client.post('/designer/projects/new/create',json=dict(project_data,accountId=designer_accounts[0],categoryId=876543))
    assert response.status_code==400 and 'categoryId' in response.json['errors']
    response=client.post(f'/designer/projects/new/{sprint_projects[0]}/update',json=dict(project_data,categoryId=876543))
    assert response.status_code==400


def test_category_html_errors_keep_input_and_success_uses_redirect(client):
    response=client.post('/manager/categories/create',headers=HTML,data={'categoryName':'  ','description':'Keep this description'})
    assert response.status_code==400 and 'Keep this description' in response.text
    response=client.post('/manager/categories/create',headers=HTML,data={'categoryName':'Japandi','description':'Warm wood.'})
    assert response.status_code==303
    detail=client.get(response.location,headers=HTML)
    assert detail.status_code==200 and 'created successfully' in detail.text
    category_id=int(response.location.rsplit('/',1)[1])
    for path in ['/manager/categories','/manager/categories/search',f'/manager/categories/{category_id}/update',f'/manager/categories/{category_id}/delete']:
        assert client.get(path,headers=HTML).status_code==200
