import pytest
from entity.projects.interior_design_project import InteriorDesignProject
from entity.shortlist.shortlist import Shortlist
from infrastructure.database import db

HTML={'Accept':'text/html'}


@pytest.mark.parametrize('query,expected',[('',3),('bedok',1),('JAPANDI',1),('bright renovation',3),('%',1),('_',0),('unmatched',0)])
def test_customer_search_matches_project_details_with_literal_keywords(client,sprint_projects,query,expected):
    response=client.get('/customer/projects',query_string={'q':' '+query+' '})
    assert response.status_code==200 and len(response.json['projects'])==expected
    assert all(p['projectId'] in sprint_projects for p in response.json['projects'])


def test_shortlist_is_unique_scoped_and_removed_without_deleting_project(app,client,sprint_projects,portal_accounts):
    first=sprint_projects[0]; a=portal_accounts['customer1']; b=portal_accounts['customer2']
    path=f'/customer/projects/{first}/shortlist'
    assert client.post(path,json={'accountId':a}).status_code==201
    assert client.post(path,json={'accountId':a}).status_code==400
    assert client.post(path,json={'accountId':b}).status_code==201
    assert len(client.get('/customer/shortlist',query_string={'accountId':a}).json['projects'])==1
    assert client.get('/customer/shortlist',query_string={'accountId':b,'q':'quiet'}).json['projects']==[]
    assert client.get(f'/customer/shortlist/{sprint_projects[1]}',query_string={'accountId':a}).status_code==404
    assert client.get(f'/customer/shortlist/{first}',query_string={'accountId':a}).status_code==200
    assert client.post(f'/customer/shortlist/{first}/remove',json={'accountId':a}).status_code==200
    assert client.get('/customer/shortlist',query_string={'accountId':a}).json['projects']==[]
    with app.app_context():
        assert InteriorDesignProject.getProject(first) is not None
        assert Shortlist.getShortlistCount(first)==1
    assert client.post(f'/customer/shortlist/{first}/remove',json={'accountId':a}).status_code==404


def test_customer_views_increment_and_designer_reads_do_not(app,client,sprint_projects,portal_accounts):
    project_id=sprint_projects[0]; owner=portal_accounts['customer1']
    with app.app_context(): assert InteriorDesignProject.getViewCount(project_id)==0
    assert client.get('/customer/projects').status_code==200
    assert client.get(f'/designer/projects/new/{project_id}').status_code==200
    assert client.get(f'/designer/projects/{project_id}/views').json['count']==0
    assert client.get(f'/customer/projects/{project_id}').status_code==200
    assert client.get(f'/customer/projects/{project_id}').status_code==200
    assert client.post(f'/customer/projects/{project_id}/shortlist',json={'accountId':owner}).status_code==201
    assert client.get(f'/customer/shortlist/{project_id}',query_string={'accountId':owner}).status_code==200
    assert client.get(f'/designer/projects/{project_id}/views').json['count']==3
    assert client.get(f'/designer/projects/{project_id}/shortlists').json['count']==1
    assert client.get(f'/designer/projects/{project_id}/views').json['count']==3
    assert client.get('/designer/projects/999999/views').status_code==404
    assert client.get('/customer/projects/999999').status_code==404
    response=client.get('/designer/interest/views',query_string={'accountId':portal_accounts['designer1']})
    assert len(response.json['projects'])==2
    assert sum(p['viewCount'] for p in response.json['projects'])==3


def test_project_delete_cascades_shortlist_rows(app,client,sprint_projects,portal_accounts):
    project_id=sprint_projects[0]
    assert client.post(f'/customer/projects/{project_id}/shortlist',json={'accountId':portal_accounts['customer1']}).status_code==201
    assert client.post(f'/designer/projects/new/{project_id}/delete').status_code==200
    with app.app_context(): assert Shortlist.getShortlistCount(project_id)==0
    assert client.get('/customer/shortlist',query_string={'accountId':portal_accounts['customer1']}).json['projects']==[]


def test_customer_html_links_keep_account_context_and_shortlist_actions_redirect(client,sprint_projects,portal_accounts):
    owner=portal_accounts['customer1']; project_id=sprint_projects[0]
    for path in ['/customer','/customer/projects','/customer/shortlist',f'/customer/projects/{project_id}']:
        response=client.get(path,query_string={'accountId':owner},headers=HTML)
        assert response.status_code==200 and f'accountId={owner}' in response.text
    response=client.post(f'/customer/projects/{project_id}/shortlist',data={'accountId':owner},headers=HTML)
    assert response.status_code==303
    assert 'saved to your shortlist' in client.get(response.location,headers=HTML).text
    assert client.get(f'/customer/shortlist/{project_id}',query_string={'accountId':owner},headers=HTML).status_code==200
    assert client.post(f'/customer/shortlist/{project_id}/remove',data={'accountId':owner},headers=HTML).status_code==303
    assert client.get('/customer/shortlist',headers=HTML).status_code==400
    for path in ['/designer/interest/views','/designer/interest/shortlists',f'/designer/projects/{project_id}/views',f'/designer/projects/{project_id}/shortlists']:
        response=client.get(path,query_string={'accountId':portal_accounts['designer1']},headers=HTML)
        assert response.status_code==200


@pytest.mark.parametrize('value',[None,True,'missing',0,{},[]])
def test_shortlist_rejects_bad_context_or_missing_records(client,sprint_projects,value):
    response=client.post(f'/customer/projects/{sprint_projects[0]}/shortlist',json={'accountId':value})
    assert response.status_code in (400,404)
