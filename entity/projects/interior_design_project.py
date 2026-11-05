from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from infrastructure.database import db
from entity.accounts.user_account import UserAccount


class InteriorDesignProject(db.Model):
    __tablename__ = 'interior_design_project'

    project_id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.String(32), db.ForeignKey('user_account.account_id', ondelete='RESTRICT'), nullable=False, index=True)
    project_name = db.Column(db.String(150), nullable=False)
    # Category records/lookup belong to later stories; this is a stored positive ID for now.
    category_id = db.Column(db.Integer, nullable=False)
    property_type = db.Column(db.String(100), nullable=False)
    area = db.Column(db.String(100), nullable=False)
    renovation_cost = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    project_status = db.Column(db.String(10), nullable=False)
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
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        try:
            if UserAccount.getUserAccount(accountId) is None:
                return self._reject('Account not found.', {'accountId': ['Account not found.']}, 'not_found')
            if self._name_exists(accountId, projectName, status):
                message = f'A {status.lower()} project with this name already exists for this account.'
                return self._reject(message, {'projectName': [message]})
            self.account_id, self.project_name, self.category_id = accountId, projectName, categoryId
            self.property_type, self.area, self.renovation_cost = propertyType, area, renovationCost
            self.description, self.project_status = description, status
            db.session.add(self)
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
        return db.session.execute(db.select(cls).where(
            cls.project_id == projectId, cls.project_status == status)).scalar_one_or_none()

    def _update(self, status, projectId, projectName, categoryId, propertyType, area, renovationCost, description):
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        try:
            project = self._get(projectId, status)
            if project is None:
                return self._reject(f'{status} project not found.', reason='not_found')
            if self._name_exists(project.account_id, projectName, status, projectId):
                message = f'A {status.lower()} project with this name already exists for this account.'
                return self._reject(message, {'projectName': [message]})
            project.project_name, project.category_id = projectName, categoryId
            project.property_type, project.area = propertyType, area
            project.renovation_cost, project.description = renovationCost, description
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
        return db.session.execute(db.select(cls).where(cls.account_id == accountId,
            cls.project_status == status, cls.project_name.icontains(projectName, autoescape=True))
            .order_by(cls.project_name, cls.project_id)).scalars().all()

    def _delete(self, projectId, status):
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        try:
            project = self._get(projectId, status)
            if project is None:
                return self._reject(f'{status} project not found.', reason='not_found')
            db.session.delete(project)
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
