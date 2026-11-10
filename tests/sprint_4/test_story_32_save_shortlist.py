"""Sprint 4, user story 32: one successful workflow through BCE."""
import pytest
from unittest.mock import Mock
from entity.shortlist.shortlist import Shortlist

pytestmark = [pytest.mark.sprint4, pytest.mark.story32]


def test_customer_saves_project_to_shortlist(app, customer_client, customer_account, new_project, create_account, monkeypatch):
    # Invalid user input is rejected in the boundary before the controller.
    blocked = Mock(side_effect=AssertionError('Invalid input reached the controller'))
    with monkeypatch.context() as guard:
        guard.setattr('boundary.customer.save_shortlist_idp_page.SaveShortlistIDPController.saveShortlist', blocked)
        from boundary.customer.save_shortlist_idp_page import SaveShortlistIDPPage
        with app.test_request_context(headers={'Accept': 'application/json'}):
            boundary = SaveShortlistIDPPage()
            boundary.onSave('invalid')
            invalid = app.make_response(boundary.rendered_page)
        assert invalid.status_code == 400
        blocked.assert_not_called()
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
