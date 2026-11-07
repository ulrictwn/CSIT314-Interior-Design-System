import pytest
from entity.accounts.user_account import UserAccount
from entity.profile.user_profile import UserProfile
from infrastructure.database import db

PASSWORD='Sprint-Demo-Password-123'


@pytest.fixture
def portal_accounts(app,designer_accounts):
    with app.app_context():
        ids={}
        for role,username in [('Customer','customer1'),('Customer','customer2'),('Platform Management','manager1')]:
            profile=UserProfile.getProfile(role)
            if profile is None:
                profile=UserProfile(name=role,description=role+' role',status='Active',permissions=[])
                db.session.add(profile)
                db.session.commit()
            account=UserAccount()
            assert account.createUserAccount(username,username.title(),username+'@example.com',
                '+65 6123 4567',profile.profile_id,password=PASSWORD)
            ids[username]=account.account_id
        ids['designer1']=designer_accounts[0]
        return ids


@pytest.fixture
def sprint_projects(app,designer_accounts,project_data):
    from entity.projects.interior_design_project import InteriorDesignProject
    owner,other=designer_accounts
    with app.app_context():
        records=[]
        for kind,account,name,category,area in [('New',owner,'Cove%House',1,'Bedok'),
                ('Past',owner,'Quiet Courtyard',2,'Tampines'),('Past',other,'Other Studio',1,'Bishan')]:
            record=InteriorDesignProject()
            assert getattr(record,'create'+kind+'Project')(account,**dict(project_data,
                projectName=name,categoryId=category,area=area))
            records.append(record.project_id)
        return records
