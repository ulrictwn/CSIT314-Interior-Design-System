# infrastructure/validation.py: pure value checks for direct entity calls.
from infrastructure.validation import validate_project_fields, positive_integer, search_text
# infrastructure/errors.py: application error types.
from infrastructure.errors import DomainError, NotFoundError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
# infrastructure/database.py: shared SQLAlchemy database session.
from infrastructure.database import db
# entity/accounts/user_account.py: saved account lookups.
from entity.accounts.user_account import UserAccount
# entity/categories/category.py: saved category lookups.
from entity.categories.category import Category
# entity/reports/activity_event.py: dated project activity for reports.
from entity.reports.activity_event import ActivityEvent


class InteriorDesignProject(db.Model):
    __tablename__ = 'interior_design_project'

    project_id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.String(32), db.ForeignKey('user_account.account_id', ondelete='RESTRICT'), nullable=False, index=True)
    project_name = db.Column(db.String(150), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id', ondelete='RESTRICT'), nullable=False)
    property_type = db.Column(db.String(100), nullable=False)
    area = db.Column(db.String(100), nullable=False)
    renovation_cost = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    project_status = db.Column(db.String(10), nullable=False)
    view_count = db.Column(db.Integer, nullable=False, default=0, server_default='0')
    __table_args__ = (
        db.Index('uq_project_owner_status_name', account_id, project_status, db.func.lower(project_name), unique=True),
        db.CheckConstraint("project_status IN ('New', 'Past')", name='ck_project_status'),
        {'sqlite_autoincrement': True},
    )

    def createNewProject(self, accountId: str, projectName: str, categoryId: int,
                           propertyType: str, area: str, renovationCost: float, description: str) -> bool:
        """Check saved references and duplicates, then create a New project."""
        status = 'New'
        values, errors = validate_project_fields(projectName, categoryId, propertyType, area, renovationCost, description)
        if errors:
            self.error_message = 'Please correct the errors below.'
            self.field_errors = errors or {}
            self.error_reason = 'invalid_data'
            return False
        projectName, categoryId, propertyType = values['projectName'], values['categoryId'], values['propertyType']
        area, renovationCost, description = values['area'], values['renovationCost'], values['description']
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        try:
            if UserAccount.getUserAccount(accountId) is None:
                self.error_message = 'Account not found.'
                self.field_errors = {'accountId': ['Account not found.']}
                self.error_reason = 'not_found'
                return False
            category = Category.getCategory(categoryId)
            if category is None:
                self.error_message = 'Choose an existing category.'
                self.field_errors = {'categoryId': ['Category not found.']}
                self.error_reason = 'invalid_data'
                return False
            duplicate = db.session.scalar(db.select(InteriorDesignProject.project_id).where(
                InteriorDesignProject.account_id == accountId,
                InteriorDesignProject.project_status == status,
                db.func.lower(InteriorDesignProject.project_name) == projectName.lower()).limit(1))
            if duplicate is not None:
                message = f'A {status.lower()} project with this name already exists for this account.'
                self.error_message = message
                self.field_errors = {'projectName': [message]}
                self.error_reason = 'invalid_data'
                return False
            self.account_id, self.project_name, self.category_id = accountId, projectName, categoryId
            self.property_type, self.area, self.renovation_cost = propertyType, area, renovationCost
            self.description, self.project_status = description, status
            db.session.add(self)
            db.session.flush()
            ActivityEvent.record('project_'+status.lower()+'_created', self.project_id,
                                 category_id=categoryId, category_name=category.category_name)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            self.error_message = 'A project with this name already exists for this account and project type.'
            self.field_errors = {}
            self.error_reason = 'invalid_data'
            return False
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @classmethod
    def getNewProject(cls, projectId: int) -> 'InteriorDesignProject | None':
        """Retrieve a New project by ID without increasing its view count."""
        status = 'New'
        projectId = positive_integer(projectId, 'Project ID')
        return db.session.execute(db.select(cls).where(
            cls.project_id == projectId, cls.project_status == status)).scalar_one_or_none()

    def updateNewProject(self, projectId: int, projectName: str, categoryId: int,
                           propertyType: str, area: str, renovationCost: float, description: str) -> bool:
        """Check the saved New project, category and duplicate name, then update it."""
        status = 'New'
        try:
            projectId = positive_integer(projectId, 'Project ID')
        except DomainError as error:
            self.error_message = str(error)
            self.field_errors = {'projectId': [str(error)]}
            self.error_reason = 'invalid_data'
            return False
        values, errors = validate_project_fields(projectName, categoryId, propertyType, area, renovationCost, description)
        if errors:
            self.error_message = 'Please correct the errors below.'
            self.field_errors = errors or {}
            self.error_reason = 'invalid_data'
            return False
        projectName, categoryId, propertyType = values['projectName'], values['categoryId'], values['propertyType']
        area, renovationCost, description = values['area'], values['renovationCost'], values['description']
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        try:
            project = self.getNewProject(projectId)
            if project is None:
                self.error_message = f'{status} project not found.'
                self.field_errors = {}
                self.error_reason = 'not_found'
                return False
            if Category.getCategory(categoryId) is None:
                self.error_message = 'Choose an existing category.'
                self.field_errors = {'categoryId': ['Category not found.']}
                self.error_reason = 'invalid_data'
                return False
            duplicate = db.session.scalar(db.select(InteriorDesignProject.project_id).where(
                InteriorDesignProject.account_id == project.account_id,
                InteriorDesignProject.project_status == status,
                db.func.lower(InteriorDesignProject.project_name) == projectName.lower(),
                InteriorDesignProject.project_id != projectId).limit(1))
            if duplicate is not None:
                message = f'A {status.lower()} project with this name already exists for this account.'
                self.error_message = message
                self.field_errors = {'projectName': [message]}
                self.error_reason = 'invalid_data'
                return False
            project.project_name, project.category_id = projectName, categoryId
            project.property_type, project.area = propertyType, area
            project.renovation_cost, project.description = renovationCost, description
            ActivityEvent.record('project_updated', projectId)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            self.error_message = 'A project with this name already exists for this account and project type.'
            self.field_errors = {}
            self.error_reason = 'invalid_data'
            return False
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @classmethod
    def searchNewProjects(cls, accountId: str, projectName: str) -> list['InteriorDesignProject']:
        """Find the account's New projects whose names contain the search text."""
        status = 'New'
        projectName = search_text(projectName)
        return db.session.execute(db.select(cls).where(cls.account_id == accountId,
            cls.project_status == status, cls.project_name.icontains(projectName, autoescape=True))
            .order_by(cls.project_name, cls.project_id)).scalars().all()

    def deleteNewProject(self, projectId: int) -> bool:
        """Delete the selected New project and record the successful deletion."""
        status = 'New'
        try:
            projectId = positive_integer(projectId, 'Project ID')
        except DomainError as error:
            self.error_message = str(error)
            self.field_errors = {'projectId': [str(error)]}
            self.error_reason = 'invalid_data'
            return False
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        try:
            project = self.getNewProject(projectId)
            if project is None:
                self.error_message = f'{status} project not found.'
                self.field_errors = {}
                self.error_reason = 'not_found'
                return False
            db.session.delete(project)
            ActivityEvent.record('project_deleted', projectId)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            self.error_message = 'This project is still in use.'
            self.field_errors = {}
            self.error_reason = 'invalid_data'
            return False
        except SQLAlchemyError:
            db.session.rollback()
            raise

    def createPastProject(self, accountId: str, projectName: str, categoryId: int,
                           propertyType: str, area: str, renovationCost: float, description: str) -> bool:
        """Check saved references and duplicates, then create a Past project."""
        status = 'Past'
        values, errors = validate_project_fields(projectName, categoryId, propertyType, area, renovationCost, description)
        if errors:
            self.error_message = 'Please correct the errors below.'
            self.field_errors = errors or {}
            self.error_reason = 'invalid_data'
            return False
        projectName, categoryId, propertyType = values['projectName'], values['categoryId'], values['propertyType']
        area, renovationCost, description = values['area'], values['renovationCost'], values['description']
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        try:
            if UserAccount.getUserAccount(accountId) is None:
                self.error_message = 'Account not found.'
                self.field_errors = {'accountId': ['Account not found.']}
                self.error_reason = 'not_found'
                return False
            category = Category.getCategory(categoryId)
            if category is None:
                self.error_message = 'Choose an existing category.'
                self.field_errors = {'categoryId': ['Category not found.']}
                self.error_reason = 'invalid_data'
                return False
            duplicate = db.session.scalar(db.select(InteriorDesignProject.project_id).where(
                InteriorDesignProject.account_id == accountId,
                InteriorDesignProject.project_status == status,
                db.func.lower(InteriorDesignProject.project_name) == projectName.lower()).limit(1))
            if duplicate is not None:
                message = f'A {status.lower()} project with this name already exists for this account.'
                self.error_message = message
                self.field_errors = {'projectName': [message]}
                self.error_reason = 'invalid_data'
                return False
            self.account_id, self.project_name, self.category_id = accountId, projectName, categoryId
            self.property_type, self.area, self.renovation_cost = propertyType, area, renovationCost
            self.description, self.project_status = description, status
            db.session.add(self)
            db.session.flush()
            ActivityEvent.record('project_'+status.lower()+'_created', self.project_id,
                                 category_id=categoryId, category_name=category.category_name)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            self.error_message = 'A project with this name already exists for this account and project type.'
            self.field_errors = {}
            self.error_reason = 'invalid_data'
            return False
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @classmethod
    def getPastProject(cls, projectId: int) -> 'InteriorDesignProject | None':
        """Retrieve a Past project by ID without increasing its view count."""
        status = 'Past'
        projectId = positive_integer(projectId, 'Project ID')
        return db.session.execute(db.select(cls).where(
            cls.project_id == projectId, cls.project_status == status)).scalar_one_or_none()

    def updatePastProject(self, projectId: int, projectName: str, categoryId: int,
                           propertyType: str, area: str, renovationCost: float, description: str) -> bool:
        """Check the saved Past project, category and duplicate name, then update it."""
        status = 'Past'
        try:
            projectId = positive_integer(projectId, 'Project ID')
        except DomainError as error:
            self.error_message = str(error)
            self.field_errors = {'projectId': [str(error)]}
            self.error_reason = 'invalid_data'
            return False
        values, errors = validate_project_fields(projectName, categoryId, propertyType, area, renovationCost, description)
        if errors:
            self.error_message = 'Please correct the errors below.'
            self.field_errors = errors or {}
            self.error_reason = 'invalid_data'
            return False
        projectName, categoryId, propertyType = values['projectName'], values['categoryId'], values['propertyType']
        area, renovationCost, description = values['area'], values['renovationCost'], values['description']
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        try:
            project = self.getPastProject(projectId)
            if project is None:
                self.error_message = f'{status} project not found.'
                self.field_errors = {}
                self.error_reason = 'not_found'
                return False
            if Category.getCategory(categoryId) is None:
                self.error_message = 'Choose an existing category.'
                self.field_errors = {'categoryId': ['Category not found.']}
                self.error_reason = 'invalid_data'
                return False
            duplicate = db.session.scalar(db.select(InteriorDesignProject.project_id).where(
                InteriorDesignProject.account_id == project.account_id,
                InteriorDesignProject.project_status == status,
                db.func.lower(InteriorDesignProject.project_name) == projectName.lower(),
                InteriorDesignProject.project_id != projectId).limit(1))
            if duplicate is not None:
                message = f'A {status.lower()} project with this name already exists for this account.'
                self.error_message = message
                self.field_errors = {'projectName': [message]}
                self.error_reason = 'invalid_data'
                return False
            project.project_name, project.category_id = projectName, categoryId
            project.property_type, project.area = propertyType, area
            project.renovation_cost, project.description = renovationCost, description
            ActivityEvent.record('project_updated', projectId)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            self.error_message = 'A project with this name already exists for this account and project type.'
            self.field_errors = {}
            self.error_reason = 'invalid_data'
            return False
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @classmethod
    def searchPastProjects(cls, accountId: str, projectName: str) -> list['InteriorDesignProject']:
        """Find the account's Past projects whose names contain the search text."""
        status = 'Past'
        projectName = search_text(projectName)
        return db.session.execute(db.select(cls).where(cls.account_id == accountId,
            cls.project_status == status, cls.project_name.icontains(projectName, autoescape=True))
            .order_by(cls.project_name, cls.project_id)).scalars().all()

    def deletePastProject(self, projectId: int) -> bool:
        """Delete the selected Past project and record the successful deletion."""
        status = 'Past'
        try:
            projectId = positive_integer(projectId, 'Project ID')
        except DomainError as error:
            self.error_message = str(error)
            self.field_errors = {'projectId': [str(error)]}
            self.error_reason = 'invalid_data'
            return False
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        try:
            project = self.getPastProject(projectId)
            if project is None:
                self.error_message = f'{status} project not found.'
                self.field_errors = {}
                self.error_reason = 'not_found'
                return False
            db.session.delete(project)
            ActivityEvent.record('project_deleted', projectId)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            self.error_message = 'This project is still in use.'
            self.field_errors = {}
            self.error_reason = 'invalid_data'
            return False
        except SQLAlchemyError:
            db.session.rollback()
            raise


    @classmethod
    def search_all_IDPs(cls, keyword: str) -> list['InteriorDesignProject']:
        """Search project and category details across all designers."""
        keyword = search_text(keyword)
        return db.session.scalars(db.select(cls).join(Category).where(db.or_(cls.project_name.icontains(keyword, autoescape=True),
            cls.description.icontains(keyword, autoescape=True), cls.property_type.icontains(keyword, autoescape=True),
            cls.area.icontains(keyword, autoescape=True), Category.category_name.icontains(keyword, autoescape=True),
            (db.literal('IDP') + db.cast(cls.project_id, db.String)).icontains(keyword, autoescape=True)))
                                  .order_by(cls.project_name, cls.project_id)).all()

    @classmethod
    def search_shortlist_IDP(cls, accountId: str, keyword: str) -> list['InteriorDesignProject']:
        """Search only projects saved by the specified customer."""
        keyword = search_text(keyword)
        # entity/shortlist/shortlist.py: saved customer-project relationships.
        from entity.shortlist.shortlist import Shortlist
        return db.session.scalars(db.select(cls).join(Category).join(Shortlist,
            Shortlist.project_id == cls.project_id).where(Shortlist.account_id == accountId, db.or_(cls.project_name.icontains(keyword, autoescape=True),
            cls.description.icontains(keyword, autoescape=True), cls.property_type.icontains(keyword, autoescape=True),
            cls.area.icontains(keyword, autoescape=True), Category.category_name.icontains(keyword, autoescape=True),
            (db.literal('IDP') + db.cast(cls.project_id, db.String)).icontains(keyword, autoescape=True)))
            .order_by(cls.project_name, cls.project_id)).all()

    @classmethod
    def getProject(cls, projectId):
        """Retrieve a project for ownership checks and interest-page labels."""
        projectId = positive_integer(projectId, 'Project ID')
        return db.session.get(cls, projectId)

    @classmethod
    def getIDP(cls, projectId: int) -> 'InteriorDesignProject | None':
        """Retrieve a customer-visible project and increase its view count."""
        projectId = positive_integer(projectId, 'Project ID')
        project = db.session.get(cls, projectId)
        if project is not None:
            cls.incrementViewCount(projectId)
        return project

    @classmethod
    def incrementViewCount(cls, projectId: int) -> None:
        """Increase the saved view count and record a successful project view."""
        projectId = positive_integer(projectId, 'Project ID')
        db.session.execute(db.update(cls).where(cls.project_id == projectId).values(view_count=cls.view_count+1))
        ActivityEvent.record('project_viewed', projectId)
        db.session.commit()

    @classmethod
    def getShortlistedIDP(cls, accountId, projectId):
        """Check saved membership before opening and counting a shortlisted project view."""
        projectId = positive_integer(projectId, 'Project ID')
        # entity/shortlist/shortlist.py: saved customer-project relationships.
        from entity.shortlist.shortlist import Shortlist
        return cls.getIDP(projectId) if Shortlist.contains(accountId, projectId) else None

    @classmethod
    def getViewCount(cls, projectId: int) -> int:
        """Return the saved project view count, or zero when no record exists."""
        projectId = positive_integer(projectId, 'Project ID')
        count = db.session.scalar(db.select(cls.view_count).where(cls.project_id == projectId))
        return 0 if count is None else count

    @classmethod
    def projectInterest(cls, accountId):
        """Collect the designer's projects and their view and shortlist counts."""
        # entity/shortlist/shortlist.py: saved customer-project relationships.
        from entity.shortlist.shortlist import Shortlist
        counts = db.select(Shortlist.project_id, db.func.count().label('total')).group_by(Shortlist.project_id).subquery()
        records = db.session.execute(db.select(cls, db.func.coalesce(counts.c.total, 0))
            .outerjoin(counts, counts.c.project_id == cls.project_id).where(cls.account_id == accountId)
            .order_by(cls.project_name, cls.project_id)).all()
        return [dict(projectId=p.project_id, projectName=p.project_name, status=p.project_status,
                     viewCount=p.view_count, shortlistCount=count) for p,count in records]

    def as_public_dict(self):
        """Prepare project, category and company details for customer displays."""
        # entity/company/company_profile.py: company records and database operations.
        from entity.company.company_profile import CompanyProfile
        category = Category.getCategory(self.category_id)
        owner = UserAccount.getUserAccount(self.account_id)
        company = CompanyProfile.getCompanyProfile(self.account_id)
        return dict(projectId=self.project_id, projectName=self.project_name, accountId=self.account_id,
            categoryId=self.category_id, categoryName=category.category_name if category else 'Uncategorised',
            propertyType=self.property_type, area=self.area, renovationCost=self.renovation_cost,
            description=self.description, status=self.project_status,
            designerName=owner.full_name if owner else '', companyName=company.company_name if company else '')

    @classmethod
    def checkOwnership(cls, accountId, projectId):
        """Verify that the saved project belongs to the signed-in designer."""
        project = cls.getProject(projectId)
        if project is None:
            raise NotFoundError('Project not found.')
        if project.account_id != accountId:
            # infrastructure/errors.py: application error types.
            from infrastructure.errors import AccessDeniedError
            raise AccessDeniedError('This project belongs to another designer.')
