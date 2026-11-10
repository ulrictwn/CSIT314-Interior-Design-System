# entity/validation.py: entity-owned field and value checks.
from entity.validation import validate_report_dates, positive_integer
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
# infrastructure/database.py: the shared SQLAlchemy database connection.
from infrastructure.database import db
# infrastructure/errors.py: saved-data and validation errors.
from infrastructure.errors import DomainError
# infrastructure/time.py: UTC timestamp defaults.
from infrastructure.time import utcnow
# entity/reports/activity_event.py: dated activity records used by reports.
from entity.reports.activity_event import ActivityEvent

SINGAPORE = ZoneInfo('Asia/Singapore')


class Report(db.Model):
    """Stored report snapshots shared by the three report BCE controllers."""
    __tablename__ = 'report'

    report_id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(db.String(10), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    generated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    account_id = db.Column(db.String(32), db.ForeignKey('user_account.account_id', ondelete='SET NULL'))
    totals = db.Column(db.JSON, nullable=False)
    rows = db.Column(db.JSON, nullable=False)
    __table_args__ = (
        db.CheckConstraint("report_type IN ('daily', 'weekly', 'monthly')", name='ck_report_type'),
        db.CheckConstraint('end_date >= start_date', name='ck_report_date_range'),
    )

    def generateReport(self, reportType: str, startDate: date, endDate: date) -> 'Report':
        """Validate the period and save new-IDP, shortlist and top-category totals."""
        if reportType not in ('daily', 'weekly', 'monthly'):
            raise DomainError('Choose a supported report type.')
        startDate, endDate = validate_report_dates(reportType, startDate, endDate)
        # entity/accounts/user_account.py: saved account data and credential checks.
        from entity.accounts.user_account import UserAccount
        if self.account_id and UserAccount.getUserAccount(self.account_id) is None:
            raise DomainError('Account not found.')
        start = datetime.combine(startDate, time.min, SINGAPORE).astimezone(timezone.utc)
        stop = datetime.combine(endDate + timedelta(days=1), time.min, SINGAPORE).astimezone(timezone.utc)
        period = (ActivityEvent.occurred_at >= start, ActivityEvent.occurred_at < stop)
        projects_created = db.session.scalar(db.select(db.func.count()).select_from(ActivityEvent)
            .where(*period, ActivityEvent.kind == 'project_new_created'))
        shortlist_saves = db.session.scalar(db.select(db.func.count()).select_from(ActivityEvent)
            .where(*period, ActivityEvent.kind == 'shortlist_saved'))

        # entity/categories/category.py: saved IDP category data.
        from entity.categories.category import Category
        # Rank by new IDPs created, as specified by the report wireframes.
        # Keep the creation category even if a project is later moved or deleted.
        category_name = db.func.coalesce(Category.category_name,
            db.func.max(ActivityEvent.category_name), 'Unknown category')
        category_total = db.func.count()
        categories = db.session.execute(db.select(category_name, category_total)
            .select_from(ActivityEvent)
            .outerjoin(Category, Category.category_id == ActivityEvent.category_id)
            .where(*period, ActivityEvent.kind == 'project_new_created')
            .group_by(ActivityEvent.category_id, Category.category_name)
            .order_by(category_total.desc(), db.func.lower(category_name), ActivityEvent.category_id)).all()
        totals = dict(projectsCreated=projects_created, shortlistSaves=shortlist_saves,
                      topCategory=categories[0][0] if categories else None)
        rows = [dict(area='IDP categories', activity=name, total=total) for name, total in categories]
        report = Report(report_type=reportType, start_date=startDate, end_date=endDate,
                        account_id=self.account_id, totals=totals, rows=rows)
        db.session.add(report)
        db.session.commit()
        return report

    @classmethod
    def getReport(cls, reportId):
        """Retrieve an existing report snapshot using its database ID."""
        reportId = positive_integer(reportId, 'Report ID')
        return db.session.get(cls, reportId)

    @classmethod
    def dashboard(cls):
        """Read category/project totals and the latest report for the manager dashboard."""
        # entity/categories/category.py: saved IDP category data.
        from entity.categories.category import Category
        # entity/projects/interior_design_project.py: saved project data.
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
        """Format the saved report snapshot and Singapore timestamp for display."""
        generated = self.generated_at
        if generated.tzinfo is None:
            generated = generated.replace(tzinfo=timezone.utc)
        return dict(reportId=self.report_id, type=self.report_type, startDate=self.start_date.isoformat(),
            endDate=self.end_date.isoformat(), generatedAt=generated.astimezone(SINGAPORE).strftime('%d %b %Y, %H:%M SGT'),
            accountId=self.account_id, totals=self.totals, rows=self.rows)
