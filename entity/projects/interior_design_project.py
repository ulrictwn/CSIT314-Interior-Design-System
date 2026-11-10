from entity.projects.validation import validate_project_fields
from entity.validation import positive_integer, search_text
from infrastructure.errors import DomainError, NotFoundError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from infrastructure.database import db
from entity.accounts.user_account import UserAccount
from entity.categories.category import Category
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

    def _reject(self, message, field_errors=None, reason='invalid_data') -> bool:
        self.error_message, self.field_errors, self.error_reason = message, field_errors or {}, reason
        return False

    @classmethod
    def _name_exists(cls, accountId, projectName, status, exclude_id=None):
        statement = db.select(cls.project_id).where(cls.account_id == accountId,
            cls.project_status == status, db.func.lower(cls.project_name) == projectName.lower())
        if exclude_id is not None:
            statement = statement.where(cls.project_id != exclude_id)
        return db.session.execute(statement.limit(1)).first() is not None

    def _create(self, status, accountId, projectName, categoryId, propertyType, area, renovationCost, description):
        values, errors = validate_project_fields(projectName, categoryId, propertyType, area, renovationCost, description)
        if errors:
            return self._reject('Please correct the errors below.', errors)
        projectName, categoryId, propertyType = values['projectName'], values['categoryId'], values['propertyType']
        area, renovationCost, description = values['area'], values['renovationCost'], values['description']
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        try:
            if UserAccount.getUserAccount(accountId) is None:
                return self._reject('Account not found.', {'accountId': ['Account not found.']}, 'not_found')
            category = Category.getCategory(categoryId)
            if category is None:
                return self._reject('Choose an existing category.', {'categoryId':['Category not found.']})
            if self._name_exists(accountId, projectName, status):
                message = f'A {status.lower()} project with this name already exists for this account.'
                return self._reject(message, {'projectName': [message]})
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
            return self._reject('A project with this name already exists for this account and project type.')
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @classmethod
    def _get(cls, projectId, status):
        projectId = positive_integer(projectId, 'Project ID')
        return db.session.execute(db.select(cls).where(
            cls.project_id == projectId, cls.project_status == status)).scalar_one_or_none()

    def _update(self, status, projectId, projectName, categoryId, propertyType, area, renovationCost, description):
        try:
            projectId = positive_integer(projectId, 'Project ID')
        except DomainError as error:
            return self._reject(str(error), {'projectId': [str(error)]})
        values, errors = validate_project_fields(projectName, categoryId, propertyType, area, renovationCost, description)
        if errors:
            return self._reject('Please correct the errors below.', errors)
        projectName, categoryId, propertyType = values['projectName'], values['categoryId'], values['propertyType']
        area, renovationCost, description = values['area'], values['renovationCost'], values['description']
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        try:
            project = self._get(projectId, status)
            if project is None:
                return self._reject(f'{status} project not found.', reason='not_found')
            if Category.getCategory(categoryId) is None:
                return self._reject('Choose an existing category.', {'categoryId':['Category not found.']})
            if self._name_exists(project.account_id, projectName, status, projectId):
                message = f'A {status.lower()} project with this name already exists for this account.'
                return self._reject(message, {'projectName': [message]})
            project.project_name, project.category_id = projectName, categoryId
            project.property_type, project.area = propertyType, area
            project.renovation_cost, project.description = renovationCost, description
            ActivityEvent.record('project_updated', projectId)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return self._reject('A project with this name already exists for this account and project type.')
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @classmethod
    def _search(cls, accountId, projectName, status):
        projectName = search_text(projectName)
        return db.session.execute(db.select(cls).where(cls.account_id == accountId,
            cls.project_status == status, cls.project_name.icontains(projectName, autoescape=True))
            .order_by(cls.project_name, cls.project_id)).scalars().all()

    def _delete(self, projectId, status):
        try:
            projectId = positive_integer(projectId, 'Project ID')
        except DomainError as error:
            return self._reject(str(error), {'projectId': [str(error)]})
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        try:
            project = self._get(projectId, status)
            if project is None:
                return self._reject(f'{status} project not found.', reason='not_found')
            db.session.delete(project)
            ActivityEvent.record('project_deleted', projectId)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return self._reject('This project is still in use.')
        except SQLAlchemyError:
            db.session.rollback()
            raise

    def createNewProject(self, accountId: str, projectName: str, categoryId: int,
                           propertyType: str, area: str, renovationCost: float, description: str) -> bool:
        return self._create('New', accountId, projectName, categoryId, propertyType, area, renovationCost, description)

    @classmethod
    def getNewProject(cls, projectId: int) -> 'InteriorDesignProject | None':
        return cls._get(projectId, 'New')

    def updateNewProject(self, projectId: int, projectName: str, categoryId: int,
                           propertyType: str, area: str, renovationCost: float, description: str) -> bool:
        return self._update('New', projectId, projectName, categoryId, propertyType, area, renovationCost, description)

    @classmethod
    def searchNewProjects(cls, accountId: str, projectName: str) -> list['InteriorDesignProject']:
        return cls._search(accountId, projectName, 'New')

    def deleteNewProject(self, projectId: int) -> bool:
        return self._delete(projectId, 'New')

    def createPastProject(self, accountId: str, projectName: str, categoryId: int,
                           propertyType: str, area: str, renovationCost: float, description: str) -> bool:
        return self._create('Past', accountId, projectName, categoryId, propertyType, area, renovationCost, description)

    @classmethod
    def getPastProject(cls, projectId: int) -> 'InteriorDesignProject | None':
        return cls._get(projectId, 'Past')

    def updatePastProject(self, projectId: int, projectName: str, categoryId: int,
                           propertyType: str, area: str, renovationCost: float, description: str) -> bool:
        return self._update('Past', projectId, projectName, categoryId, propertyType, area, renovationCost, description)

    @classmethod
    def searchPastProjects(cls, accountId: str, projectName: str) -> list['InteriorDesignProject']:
        return cls._search(accountId, projectName, 'Past')

    def deletePastProject(self, projectId: int) -> bool:
        return self._delete(projectId, 'Past')

    @classmethod
    def _keyword_filter(cls, keyword):
        return db.or_(cls.project_name.icontains(keyword, autoescape=True),
            cls.description.icontains(keyword, autoescape=True), cls.property_type.icontains(keyword, autoescape=True),
            cls.area.icontains(keyword, autoescape=True), Category.category_name.icontains(keyword, autoescape=True),
            (db.literal('IDP') + db.cast(cls.project_id, db.String)).icontains(keyword, autoescape=True))

    @classmethod
    def search_all_IDPs(cls, keyword: str) -> list['InteriorDesignProject']:
        keyword = search_text(keyword)
        return db.session.scalars(db.select(cls).join(Category).where(cls._keyword_filter(keyword))
                                  .order_by(cls.project_name, cls.project_id)).all()

    @classmethod
    def search_shortlist_IDP(cls, accountId: str, keyword: str) -> list['InteriorDesignProject']:
        keyword = search_text(keyword)
        from entity.shortlist.shortlist import Shortlist
        return db.session.scalars(db.select(cls).join(Category).join(Shortlist,
            Shortlist.project_id == cls.project_id).where(Shortlist.account_id == accountId, cls._keyword_filter(keyword))
            .order_by(cls.project_name, cls.project_id)).all()

    @classmethod
    def getProject(cls, projectId):
        projectId = positive_integer(projectId, 'Project ID')
        return db.session.get(cls, projectId)

    @classmethod
    def getIDP(cls, projectId: int) -> 'InteriorDesignProject | None':
        projectId = positive_integer(projectId, 'Project ID')
        project = db.session.get(cls, projectId)
        if project is not None:
            cls.incrementViewCount(projectId)
        return project

    @classmethod
    def incrementViewCount(cls, projectId: int) -> None:
        projectId = positive_integer(projectId, 'Project ID')
        db.session.execute(db.update(cls).where(cls.project_id == projectId).values(view_count=cls.view_count+1))
        ActivityEvent.record('project_viewed', projectId)
        db.session.commit()

    @classmethod
    def getShortlistedIDP(cls, accountId, projectId):
        projectId = positive_integer(projectId, 'Project ID')
        from entity.shortlist.shortlist import Shortlist
        return cls.getIDP(projectId) if Shortlist.contains(accountId, projectId) else None

    @classmethod
    def getViewCount(cls, projectId: int) -> int:
        projectId = positive_integer(projectId, 'Project ID')
        count = db.session.scalar(db.select(cls.view_count).where(cls.project_id == projectId))
        return 0 if count is None else count

    @classmethod
    def projectInterest(cls, accountId):
        from entity.shortlist.shortlist import Shortlist
        counts = db.select(Shortlist.project_id, db.func.count().label('total')).group_by(Shortlist.project_id).subquery()
        records = db.session.execute(db.select(cls, db.func.coalesce(counts.c.total, 0))
            .outerjoin(counts, counts.c.project_id == cls.project_id).where(cls.account_id == accountId)
            .order_by(cls.project_name, cls.project_id)).all()
        return [dict(projectId=p.project_id, projectName=p.project_name, status=p.project_status,
                     viewCount=p.view_count, shortlistCount=count) for p,count in records]

    def as_public_dict(self):
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
        project = cls.getProject(projectId)
        if project is None:
            raise NotFoundError('Project not found.')
        if project.account_id != accountId:
            from infrastructure.errors import AccessDeniedError
            raise AccessDeniedError('This project belongs to another designer.')
