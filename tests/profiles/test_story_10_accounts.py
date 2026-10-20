import pytest
pytestmark=pytest.mark.story10

@pytest.mark.parametrize('query',['','   ','CU101','cUsToMeR1','Name customer1'])
def test_TC59_search_account_id_username_name_and_blank(admin_client,create_account,query):
    create_account()
    response=admin_client.get('/accounts/search',query_string={'q':query})
    assert response.status_code==200
    html=response.get_data(as_text=True)
    assert 'CU101' in html
    assert ('href="/accounts/UA101"' in html)==(not query.strip())

def test_TC60_no_matching_account_has_empty_message(admin_client,create_account):
    create_account()
    response=admin_client.get('/accounts/search?q=no-matching-account')
    assert response.status_code==200 and 'No accounts found.' in response.get_data(as_text=True)
