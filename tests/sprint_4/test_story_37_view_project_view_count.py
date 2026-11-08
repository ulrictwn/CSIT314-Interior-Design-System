"""Sprint 4, user story 37: one successful workflow through BCE."""
import pytest
from entity.projects.interior_design_project import InteriorDesignProject
from infrastructure.database import db

pytestmark = [pytest.mark.sprint4, pytest.mark.story37]


def test_designer_views_saved_project_view_count(app, client, new_project):
    with app.app_context():
        InteriorDesignProject.getNewProject(new_project).view_count = 3
        db.session.commit()
    response = client.get(f'/designer/projects/{new_project}/views')
    assert response.status_code == 200
    assert response.json['project']['projectId'] == new_project
    assert response.json['count'] == 3
