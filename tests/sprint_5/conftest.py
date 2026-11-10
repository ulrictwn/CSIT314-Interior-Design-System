"""Entity-created activity matching TC63–TC65 in the updated project document."""
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
        living, transitional, kitchen, reassignment = Category(), Category(), Category(), Category()
        assert living.createCategory('Bohemian Living room', 'Layered, colourful living spaces.')
        assert transitional.createCategory('Transitional Kitchen', 'Classic and modern kitchen details.')
        assert kitchen.createCategory('Bohemian Kitchen', 'Warm, eclectic kitchen spaces.')
        assert reassignment.createCategory('Japandi', 'Warm, minimalist interiors.')
        living_id, transitional_id = living.category_id, transitional.category_id
        kitchen_id, reassignment_id = kitchen.category_id, reassignment.category_id

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

        def saves(project_id, stamps):
            for index, stamp in enumerate(stamps):
                assert Shortlist().saveShortlist(customer, project_id)
                set_event_time('shortlist_saved', project_id, stamp)
                if index < len(stamps) - 1:
                    assert Shortlist().removeShortlist(customer, project_id)

        # TC63 includes the first and last instants of 4 November in Singapore.
        november_first = datetime(2026, 11, 3, 16, tzinfo=timezone.utc)
        november_last = datetime(2026, 11, 4, 15, 59, 59, 999999, tzinfo=timezone.utc)
        deleted = project('Bohemian Living Home', living_id, november_first)
        reassigned = project('Bohemian Living Apartment', living_id, november_last)
        saves(deleted, [november_first])
        saves(reassigned, [november_last])

        # TC64: one new project and eight save actions during 1–7 June.
        june_first = datetime(2026, 5, 31, 16, tzinfo=timezone.utc)
        june_week_last = datetime(2026, 6, 7, 15, 59, 59, 999999, tzinfo=timezone.utc)
        weekly_project = project('Transitional Week Home', transitional_id, june_first)
        saves(weekly_project, [june_first] + [datetime(2026, 6, 5, 2, tzinfo=timezone.utc)] * 6 + [june_week_last])

        # TC65 adds nine new projects and 24 saves later in June: 10 and 32 overall.
        june_middle = datetime(2026, 6, 15, 2, tzinfo=timezone.utc)
        later_projects = [project(f'Bohemian Kitchen Home {index + 1}', kitchen_id, june_middle)
                          for index in range(6)]
        for index in range(3):
            project(f'Transitional Kitchen Home {index + 1}', transitional_id, june_middle)
        saves(later_projects[0], [june_middle] * 24)
        project('Past Bohemian Home', kitchen_id, june_middle, past=True)
        project('Before June', kitchen_id, datetime(2026, 5, 31, 15, 59, 59, tzinfo=timezone.utc))
        july_project = project('July Home', kitchen_id, datetime(2026, 6, 30, 16, tzinfo=timezone.utc))
        saves(july_project, [datetime(2026, 6, 30, 16, tzinfo=timezone.utc)])

        # Saved activity retains its original category after reassignment/deletion.
        assert InteriorDesignProject().updateNewProject(reassigned, 'Bohemian Living Apartment', reassignment_id,
            'Apartment', 'Bedok', 80000, 'Now assigned to another category.')
        assert InteriorDesignProject().deleteNewProject(deleted)
        assert Category().deleteCategory(living_id)
        ActivityEvent.record('login_success', customer)
        db.session.commit()
    return dict(designer=designer, transitional_id=transitional_id,
        daily=dict(totals=dict(projectsCreated=2, shortlistSaves=2, topCategory='Bohemian Living room'),
                   rows=[dict(area='IDP categories', activity='Bohemian Living room', total=2)]),
        weekly=dict(totals=dict(projectsCreated=1, shortlistSaves=8, topCategory='Transitional Kitchen'),
                    rows=[dict(area='IDP categories', activity='Transitional Kitchen', total=1)]),
        monthly=dict(totals=dict(projectsCreated=10, shortlistSaves=32, topCategory='Bohemian Kitchen'),
                     rows=[dict(area='IDP categories', activity='Bohemian Kitchen', total=6),
                           dict(area='IDP categories', activity='Transitional Kitchen', total=4)]))
