"""Sprint 4, user story 32: one successful workflow through BCE."""
import pytest
from entity.shortlist.shortlist import Shortlist

pytestmark = [pytest.mark.sprint4, pytest.mark.story32]


def test_customer_saves_project_to_shortlist(app, customer_client, customer_account, new_project, create_account):
    other_id = create_account('other_customer', 'Customer')
    response = customer_client.post(f'/customer/projects/{new_project}/shortlist', json={'accountId': other_id})
    assert response.status_code == 403
    with app.app_context():
        assert not Shortlist.contains(other_id, new_project)
    response = customer_client.post(f'/customer/projects/{new_project}/shortlist', json={'accountId': customer_account})
    assert response.status_code == 201
    with app.app_context():
        assert Shortlist.contains(customer_account, new_project)
