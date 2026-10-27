import pytest
pytestmark=pytest.mark.story10

@pytest.mark.parametrize('query',['','   ','202','cUsToMeR1','Name customer1'])
def test_TC35_search_account_id_username_name_and_blank(admin_client,create_account,query):
    create_account()
    response=admin_client.get('/accounts/search',query_string={'q':query})
    assert response.status_code==200
    html=response.get_data(as_text=True)
    assert '202' in html
    assert ('href="/accounts/101"' in html)==(not query.strip())

def test_TC36_no_matching_account_has_empty_message(admin_client,create_account):
    create_account()
    response=admin_client.get('/accounts/search?q=no-matching-account')
    assert response.status_code==200 and 'No accounts found.' in response.get_data(as_text=True)
