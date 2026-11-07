from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
from infrastructure.database import db
from infrastructure.errors import DomainError
from infrastructure.time import utcnow
from entity.reports.activity_event import ActivityEvent

SINGAPORE = ZoneInfo('Asia/Singapore')


class Report(db.Model):
    """Stored report snapshots. Stories 46–48 have no completed BCE diagrams."""
    __tablename__ = 'report'

    report_id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(db.String(10), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    generated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    account_id = db.Column(db.String(32), db.ForeignKey('user_account.account_id', ondelete='SET NULL'))
    totals = db.Column(db.JSON, nullable=False)
    rows = db.Column(db.JSON, nullable=False)

    @classmethod
    def _generate(cls, kind, startDate, endDate, accountId):
        from entity.accounts.user_account import UserAccount
        if accountId and UserAccount.getUserAccount(accountId) is None:
            raise DomainError('Account not found.')
        start = datetime.combine(startDate, time.min, SINGAPORE).astimezone(timezone.utc)
        stop = datetime.combine(endDate + timedelta(days=1), time.min, SINGAPORE).astimezone(timezone.utc)
        events = dict(db.session.execute(db.select(ActivityEvent.kind, db.func.count())
            .where(ActivityEvent.occurred_at >= start, ActivityEvent.occurred_at < stop)
            .group_by(ActivityEvent.kind)).all())
        registrations = db.session.scalar(db.select(db.func.count()).select_from(UserAccount)
            .where(UserAccount.created_at >= start, UserAccount.created_at < stop))
        totals = dict(successfulLogins=events.get('login_success', 0), newRegistrations=registrations,
                      projectsCreated=events.get('project_new_created', 0)+events.get('project_past_created', 0))
        rows = [dict(area=area, activity=label, total=events.get(event, 0)) for area, label, event in [
            ('Interior Design Projects', 'New projects created', 'project_new_created'),
            ('Interior Design Projects', 'Past projects added', 'project_past_created'),
            ('Interior Design Projects', 'Projects updated', 'project_updated'),
            ('Interior Design Projects', 'Projects deleted', 'project_deleted'),
            ('IDP categories', 'Categories created', 'category_created'),
            ('IDP categories', 'Categories updated', 'category_updated'),
            ('IDP categories', 'Categories deleted', 'category_deleted'),
            ('Customer activity', 'Project views', 'project_viewed'),
            ('Customer activity', 'Projects shortlisted', 'shortlist_saved'),
        ]]
        report = cls(report_type=kind, start_date=startDate, end_date=endDate,
                     account_id=accountId, totals=totals, rows=rows)
        db.session.add(report)
        db.session.commit()
        return report

    @classmethod
    def generateDailyReport(cls, startDate, endDate, accountId=None):
        return cls._generate('daily', startDate, endDate, accountId)

    @classmethod
    def generateWeeklyReport(cls, startDate, endDate, accountId=None):
        return cls._generate('weekly', startDate, endDate, accountId)

    @classmethod
    def generateMonthlyReport(cls, startDate, endDate, accountId=None):
        return cls._generate('monthly', startDate, endDate, accountId)

    @classmethod
    def getReport(cls, reportId):
        return db.session.get(cls, reportId)

    @classmethod
    def dashboard(cls):
        from entity.categories.category import Category
        from entity.projects.interior_design_project import InteriorDesignProject
        yesterday = datetime.now(SINGAPORE).date()-timedelta(days=1)
        start = datetime.combine(yesterday, time.min, SINGAPORE).astimezone(timezone.utc)
        stop = start+timedelta(days=1)
        latest = db.session.scalar(db.select(cls).where(cls.report_type == 'daily')
                                  .order_by(cls.generated_at.desc(), cls.report_id.desc()).limit(1))
        return dict(categoryCount=db.session.scalar(db.select(db.func.count()).select_from(Category)),
            projectCount=db.session.scalar(db.select(db.func.count()).select_from(InteriorDesignProject)),
            yesterday=yesterday.isoformat(), successfulLogins=db.session.scalar(db.select(db.func.count())
                .select_from(ActivityEvent).where(ActivityEvent.kind == 'login_success',
                    ActivityEvent.occurred_at >= start, ActivityEvent.occurred_at < stop)),
            latestReport=latest.as_dict() if latest else None)

    def as_dict(self):
        generated = self.generated_at
        if generated.tzinfo is None:
            generated = generated.replace(tzinfo=timezone.utc)
        return dict(reportId=self.report_id, type=self.report_type, startDate=self.start_date.isoformat(),
            endDate=self.end_date.isoformat(), generatedAt=generated.astimezone(SINGAPORE).strftime('%d %b %Y, %H:%M SGT'),
            accountId=self.account_id, totals=self.totals, rows=self.rows)
