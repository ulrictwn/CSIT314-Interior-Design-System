"""Migration checks run exclusively inside an independently guarded test database."""
from pathlib import Path
import pytest
from sqlalchemy import inspect,text
from sqlalchemy.exc import IntegrityError
from entity.accounts.user_account import UserAccount
from entity.categories.category import Category
from entity.projects.interior_design_project import InteriorDesignProject
from entity.shortlist.shortlist import Shortlist
from infrastructure.database import db
from infrastructure.migrations import upgrade_database


def test_upgrade_preserves_legacy_data_and_is_repeatable(app,designer_accounts,tmp_path):
    owner,_=designer_accounts
    with app.app_context():
        # Refuse table-removal setup unless the actual connected database is disposable.
        assert app.config['TESTING'] is True
        if db.engine.dialect.name=='sqlite':
            assert Path(db.engine.url.database).resolve()==(tmp_path/'profiles.sqlite').resolve()
        else:
            assert db.engine.dialect.name=='postgresql' and db.engine.url.database=='nestora_test'
            assert db.session.scalar(text('SELECT current_schema()')).startswith('profile_test_')
        account=UserAccount.getUserAccount(owner)
        before=(account.username,account.password_hash,account.email)
        db.session.remove()
        Shortlist.__table__.drop(db.engine)
        InteriorDesignProject.__table__.drop(db.engine)
        with db.engine.begin() as connection:
            connection.execute(text('CREATE TABLE interior_design_project ('
                'project_id INTEGER PRIMARY KEY, account_id VARCHAR(32) NOT NULL, project_name VARCHAR(150) NOT NULL, '
                'category_id INTEGER NOT NULL, property_type VARCHAR(100) NOT NULL, area VARCHAR(100) NOT NULL, '
                'renovation_cost FLOAT NOT NULL, description TEXT NOT NULL, project_status VARCHAR(10) NOT NULL)'))
            connection.execute(text("INSERT INTO interior_design_project VALUES (71,:owner,'Original home',444,'Apartment','Bedok',10000,'Preserve this project','Past')"),{'owner':owner})
        upgrade_database()
        upgrade_database()
        account=UserAccount.getUserAccount(owner)
        assert (account.username,account.password_hash,account.email)==before
        project=InteriorDesignProject.getProject(71)
        assert project.project_name=='Original home' and project.category_id==444 and project.view_count==0
        category=Category.getCategory(444)
        assert category.category_name=='Existing category 444'
        new=Category()
        assert new.createCategory('New category','A newly created category.')
        assert new.category_id>444
        allocated_id=new.category_id
        assert Category().deleteCategory(allocated_id)
        upgrade_database()
        replacement=Category()
        assert replacement.createCategory('Replacement category','Keep generated IDs increasing.')
        assert replacement.category_id>allocated_id
        assert {'category','shortlist','activity_event','report'}.issubset(inspect(db.engine).get_table_names())
        with pytest.raises(IntegrityError):
            db.session.execute(text('UPDATE interior_design_project SET category_id=98765 WHERE project_id=71'))
            db.session.commit()
        db.session.rollback()
        assert InteriorDesignProject.getProject(71).category_id==444
