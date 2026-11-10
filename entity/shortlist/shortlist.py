# infrastructure/validation.py: shared pure value checks.
from infrastructure.validation import positive_integer, valid_account_id
# infrastructure/errors.py: saved-data and validation errors.
from infrastructure.errors import DomainError
from sqlalchemy.exc import IntegrityError
# infrastructure/database.py: the shared SQLAlchemy database connection.
from infrastructure.database import db
# infrastructure/time.py: UTC timestamp defaults.
from infrastructure.time import utcnow
# entity/accounts/user_account.py: saved account data and credential checks.
from entity.accounts.user_account import UserAccount
# entity/reports/activity_event.py: dated activity records used by reports.
from entity.reports.activity_event import ActivityEvent


class Shortlist(db.Model):
    __tablename__ = 'shortlist'

    account_id = db.Column(db.String(32), db.ForeignKey('user_account.account_id', ondelete='CASCADE'), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('interior_design_project.project_id', ondelete='CASCADE'), primary_key=True)
    saved_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    @classmethod
    def contains(cls, accountId, projectId):
        """Check whether this account has already saved the project."""
        if not valid_account_id(accountId):
            return False
        projectId = positive_integer(projectId, 'Project ID')
        return db.session.get(cls, (accountId, projectId)) is not None

    def saveShortlist(self, accountId: str, projectId: int) -> bool:
        """Reject missing or duplicate references, then save the project."""
        try:
            projectId = positive_integer(projectId, 'Project ID')
        except DomainError as error:
            self.error_message = str(error)
            self.field_errors = {}
            self.error_reason = 'invalid_data'
            return False
        # entity/projects/interior_design_project.py: saved project data.
        from entity.projects.interior_design_project import InteriorDesignProject
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        if UserAccount.getUserAccount(accountId) is None:
            self.error_message = 'Account not found.'
            self.field_errors = {}
            self.error_reason = 'not_found'
            return False
        if db.session.get(InteriorDesignProject, projectId) is None:
            self.error_message = 'Project not found.'
            self.field_errors = {}
            self.error_reason = 'not_found'
            return False
        if self.contains(accountId, projectId):
            self.error_message = 'This project is already in your shortlist.'
            self.field_errors = {}
            self.error_reason = 'invalid_data'
            return False
        try:
            self.account_id, self.project_id = accountId, projectId
            db.session.add(self)
            ActivityEvent.record('shortlist_saved', projectId)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            self.error_message = 'This project is already shortlisted or no longer exists.'
            self.field_errors = {}
            self.error_reason = 'invalid_data'
            return False

    def removeShortlist(self, accountId: str, projectId: int) -> bool:
        """Remove the existing saved project and record the removal."""
        try:
            projectId = positive_integer(projectId, 'Project ID')
        except DomainError as error:
            self.error_message = str(error)
            self.field_errors = {}
            self.error_reason = 'invalid_data'
            return False
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        record = db.session.get(Shortlist, (accountId, projectId))
        if record is None:
            self.error_message = 'This project is not in your shortlist.'
            self.field_errors = {}
            self.error_reason = 'not_found'
            return False
        db.session.delete(record)
        ActivityEvent.record('shortlist_removed', projectId)
        db.session.commit()
        return True

    @classmethod
    def getShortlistCount(cls, projectId: int) -> int:
        """Count the accounts currently saving the project."""
        projectId = positive_integer(projectId, 'Project ID')
        return db.session.scalar(db.select(db.func.count()).select_from(cls).where(cls.project_id == projectId))

    @classmethod
    def savedProjectIds(cls, accountId):
        """Return the project IDs saved by the specified account."""
        return list(db.session.scalars(db.select(cls.project_id).where(cls.account_id == accountId))) if accountId else []

    @classmethod
    def dashboard(cls, accountId):
        """Return the saved-project total and the three most recent saves."""
        # entity/projects/interior_design_project.py: saved project data.
        from entity.projects.interior_design_project import InteriorDesignProject
        recent = db.session.scalars(db.select(InteriorDesignProject).join(cls,
            cls.project_id == InteriorDesignProject.project_id).where(cls.account_id == accountId)
            .order_by(cls.saved_at.desc(), cls.project_id.desc()).limit(3)).all() if accountId else []
        return dict(savedCount=len(cls.savedProjectIds(accountId)), recent=[p.as_public_dict() for p in recent])
