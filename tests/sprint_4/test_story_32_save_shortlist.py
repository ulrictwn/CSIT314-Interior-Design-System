"""Sprint 4, user story 32: one successful workflow through BCE."""
import pytest
from entity.shortlist.shortlist import Shortlist

pytestmark = [pytest.mark.sprint4, pytest.mark.story32]


def test_TC49_customer_saves_project_to_shortlist(app, customer_client, customer_account, new_project, create_account):
    # Invalid input passes through the controller and is rejected by the entity.
    from boundary.customer.save_shortlist_idp_page import SaveShortlistIDPPage
    with app.test_request_context(headers={'Accept': 'application/json'}):
        boundary = SaveShortlistIDPPage()
        boundary.onSave('invalid')
        invalid = app.make_response(boundary.rendered_page)
    assert invalid.status_code == 400
    with app.app_context():
        assert not Shortlist.contains(customer_account, new_project)
    other_id = create_account('other_customer', 'Customer')
    response = customer_client.post(f'/customer/projects/{new_project}/shortlist', json={'accountId': other_id})
    assert response.status_code == 403
    with app.app_context():
        assert not Shortlist.contains(other_id, new_project)
    response = customer_client.post(f'/customer/projects/{new_project}/shortlist', json={'accountId': customer_account})
    assert response.status_code == 201
    with app.app_context():
        assert Shortlist.contains(customer_account, new_project)
    duplicate = customer_client.post(f'/customer/projects/{new_project}/shortlist')
    assert duplicate.status_code == 400
    with app.app_context():
        assert Shortlist.contains(customer_account, new_project)
