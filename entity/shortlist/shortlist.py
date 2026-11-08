from entity.validation import positive_integer
from infrastructure.errors import DomainError
from sqlalchemy.exc import IntegrityError
from infrastructure.database import db
from infrastructure.time import utcnow
from entity.accounts.user_account import UserAccount
from entity.reports.activity_event import ActivityEvent


class Shortlist(db.Model):
    __tablename__ = 'shortlist'

    account_id = db.Column(db.String(32), db.ForeignKey('user_account.account_id', ondelete='CASCADE'), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('interior_design_project.project_id', ondelete='CASCADE'), primary_key=True)
    saved_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    def _reject(self, message, reason='invalid_data'):
        self.error_message, self.field_errors, self.error_reason = message, {}, reason
        return False

    @classmethod
    def contains(cls, accountId, projectId):
        return db.session.get(cls, (accountId, projectId)) is not None if accountId else False

    def saveShortlist(self, accountId: str, projectId: int) -> bool:
        try:
            projectId = positive_integer(projectId, 'Project ID')
        except DomainError as error:
            return self._reject(str(error))
        from entity.projects.interior_design_project import InteriorDesignProject
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        if UserAccount.getUserAccount(accountId) is None:
            return self._reject('Account not found.', 'not_found')
        if db.session.get(InteriorDesignProject, projectId) is None:
            return self._reject('Project not found.', 'not_found')
        if self.contains(accountId, projectId):
            return self._reject('This project is already in your shortlist.')
        try:
            self.account_id, self.project_id = accountId, projectId
            db.session.add(self)
            ActivityEvent.record('shortlist_saved', projectId)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return self._reject('This project is already shortlisted or no longer exists.')

    def removeShortlist(self, accountId: str, projectId: int) -> bool:
        try:
            projectId = positive_integer(projectId, 'Project ID')
        except DomainError as error:
            return self._reject(str(error))
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        record = db.session.get(Shortlist, (accountId, projectId))
        if record is None:
            return self._reject('This project is not in your shortlist.', 'not_found')
        db.session.delete(record)
        ActivityEvent.record('shortlist_removed', projectId)
        db.session.commit()
        return True

    @classmethod
    def getShortlistCount(cls, projectId: int) -> int:
        return db.session.scalar(db.select(db.func.count()).select_from(cls).where(cls.project_id == projectId))

    @classmethod
    def savedProjectIds(cls, accountId):
        return list(db.session.scalars(db.select(cls.project_id).where(cls.account_id == accountId))) if accountId else []

    @classmethod
    def dashboard(cls, accountId):
        from entity.projects.interior_design_project import InteriorDesignProject
        recent = db.session.scalars(db.select(InteriorDesignProject).join(cls,
            cls.project_id == InteriorDesignProject.project_id).where(cls.account_id == accountId)
            .order_by(cls.saved_at.desc(), cls.project_id.desc()).limit(3)).all() if accountId else []
        return dict(savedCount=len(cls.savedProjectIds(accountId)), recent=[p.as_public_dict() for p in recent])
