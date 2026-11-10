"""Real project/shortlist activity for the report use cases and updated wireframes."""
from datetime import datetime, timezone

import pytest
from entity.categories.category import Category
from entity.projects.interior_design_project import InteriorDesignProject
from entity.reports.activity_event import ActivityEvent
from entity.shortlist.shortlist import Shortlist
from infrastructure.database import db


@pytest.fixture
def report_activity(app, create_account):
    designer = create_account('report_designer', 'Interior Designer')
    customer = create_account('report_customer', 'Customer')
    with app.app_context():
        scandinavian, japandi = Category(), Category()
        assert scandinavian.createCategory('Scandinavian', 'Light, natural interiors.')
        assert japandi.createCategory('Japandi', 'Warm, minimalist interiors.')
        scandinavian_id, japandi_id = scandinavian.category_id, japandi.category_id

        def set_event_time(kind, target_id, stamp):
            event = db.session.scalar(db.select(ActivityEvent).where(
                ActivityEvent.kind == kind, ActivityEvent.target_id == str(target_id))
                .order_by(ActivityEvent.event_id.desc()).limit(1))
            event.occurred_at = stamp
            db.session.commit()

        def project(name, category_id, stamp, past=False):
            record = InteriorDesignProject()
            create = record.createPastProject if past else record.createNewProject
            assert create(designer, name, category_id, 'Apartment', 'Bedok', 80000, 'Report example.')
            set_event_time('project_past_created' if past else 'project_new_created', record.project_id, stamp)
            return record.project_id

        # The first and last instants of 5 June in Singapore both count.
        first = datetime(2026, 6, 4, 16, tzinfo=timezone.utc)
        middle = datetime(2026, 6, 5, 2, tzinfo=timezone.utc)
        last = datetime(2026, 6, 5, 15, 59, 59, 999999, tzinfo=timezone.utc)
        deleted = project('Nordic Home', scandinavian_id, first)
        reassigned = project('Nordic Apartment', scandinavian_id, middle)
        existing = project('Japandi Home', japandi_id, last)
        project('Past Japandi Home', japandi_id, middle, past=True)
        project('Before June', japandi_id, datetime(2026, 5, 31, 15, 59, 59, tzinfo=timezone.utc))
        project('July Home', japandi_id, datetime(2026, 6, 30, 16, tzinfo=timezone.utc))

        # Three save actions count, including a save removed and saved again.
        assert Shortlist().saveShortlist(customer, deleted)
        set_event_time('shortlist_saved', deleted, first)
        assert Shortlist().removeShortlist(customer, deleted)
        assert Shortlist().saveShortlist(customer, deleted)
        set_event_time('shortlist_saved', deleted, middle)
        assert Shortlist().saveShortlist(customer, existing)
        set_event_time('shortlist_saved', existing, last)
        outside = db.session.scalar(db.select(InteriorDesignProject).where(
            InteriorDesignProject.project_name == 'July Home'))
        assert Shortlist().saveShortlist(customer, outside.project_id)
        set_event_time('shortlist_saved', outside.project_id, datetime(2026, 6, 30, 16, tzinfo=timezone.utc))

        # Reports retain the creation category after reassignment and deletion.
        assert InteriorDesignProject().updateNewProject(reassigned, 'Nordic Apartment', japandi_id,
            'Apartment', 'Bedok', 80000, 'Now assigned to another category.')
        assert InteriorDesignProject().deleteNewProject(deleted)
        assert Category().deleteCategory(scandinavian_id)
        ActivityEvent.record('login_success', customer)
        db.session.commit()
    return dict(designer=designer, japandi_id=japandi_id,
                totals=dict(projectsCreated=3, shortlistSaves=3, topCategory='Scandinavian'),
                rows=[dict(area='IDP categories', activity='Scandinavian', total=2),
                      dict(area='IDP categories', activity='Japandi', total=1)])
