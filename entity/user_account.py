from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from infrastructure.database import db
from infrastructure.errors import DomainError
from infrastructure.permissions import ADMIN_PERMISSIONS
from infrastructure.time import utcnow

_DUMMY_HASH = generate_password_hash('not-an-actual-account-password')
_UNSET_PASSWORD_HASH = '!'
_GLOBAL_ACCOUNT_COUNTER = '*'


class AccountIdCounter(db.Model):
    """The '*' row allocates account numbers shared by every profile."""
    __tablename__ = 'account_id_counter'
    prefix = db.Column(db.String(2), primary_key=True)
    next_number = db.Column(db.Integer, nullable=False, default=1)


class UserAccount(db.Model):
    __tablename__ = 'user_account'
    account_id = db.Column(db.String(32), primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False, default=_UNSET_PASSWORD_HASH)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(254), nullable=False, unique=True)
    phone_number = db.Column(db.String(40), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey('user_profile.profile_id', ondelete='RESTRICT'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Active')
    auth_version = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    profile = db.relationship('UserProfile')
    __table_args__ = (
        db.Index('uq_account_username_lower', db.func.lower(username), unique=True),
        db.Index('uq_account_email_lower', db.func.lower(email), unique=True),
    )

    @property
    def active(self):
        return self.status == 'Active' and self.profile.status == 'Active'

    @property
    def is_admin(self):
        return self.profile.name.strip().casefold() == 'user admin'

    def has_permission(self, permission):
        return self.active and self.is_admin and permission in (self.profile.permissions or [])

    @property
    def has_password(self):
        return bool(self.password_hash and self.password_hash != _UNSET_PASSWORD_HASH)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        matched = check_password_hash(self.password_hash if self.has_password else _DUMMY_HASH, password)
        return self.has_password and matched

    @classmethod
    def userAccountExists(cls, username):
        return db.session.execute(db.select(cls.account_id).where(
            db.func.lower(cls.username) == username.strip().lower()).limit(1)).first() is not None

    @classmethod
    def getByUsername(cls, username):
        return db.session.execute(db.select(cls).where(
            db.func.lower(cls.username) == username.strip().lower())).scalar_one_or_none()

    @classmethod
    def getUserAccount(cls, accountId):
        return db.session.get(cls, accountId)

    @classmethod
    def generateAccountId(cls, profileId):
        """Combine the profile's actual ID with a shared, minimum-two-digit number.

        The counter is locked until the account creation transaction commits.
        Existing accounts keep their IDs; legacy per-role counters are ignored.
        """
        from entity.user_profile import UserProfile
        profile = db.session.execute(db.select(UserProfile).where(
            UserProfile.profile_id == profileId).with_for_update()).scalar_one_or_none()
        if profile is None or profile.status != 'Active':
            raise DomainError('Assign an active user profile.')
        dialect = db.engine.dialect.name
        if dialect == 'postgresql':
            from sqlalchemy.dialects.postgresql import insert
        elif dialect == 'sqlite':
            from sqlalchemy.dialects.sqlite import insert
        else:
            raise RuntimeError('Use PostgreSQL or the local SQLite preview.')
        # Existing installations start after their current account count. The
        # insert-on-conflict and row lock serialize the very first allocation too.
        initial_number = db.session.scalar(db.select(db.func.count()).select_from(cls)) + 1
        db.session.execute(insert(AccountIdCounter).values(
            prefix=_GLOBAL_ACCOUNT_COUNTER, next_number=initial_number)
                           .on_conflict_do_nothing(index_elements=['prefix']))
        counter = db.session.execute(db.select(AccountIdCounter).where(
            AccountIdCounter.prefix == _GLOBAL_ACCOUNT_COUNTER).with_for_update()
            .execution_options(populate_existing=True)).scalar_one()
        while True:
            account_id = f'{profile.profile_id}{counter.next_number:02d}'
            counter.next_number += 1
            # Beyond 99, variable-length profile IDs can form the same string
            # (profile 11 + 01 and profile 1 + 101). Skip occupied IDs safely.
            if db.session.get(cls, account_id) is None:
                return account_id

    @classmethod
    def createUserAccount(cls, username, fullName, email, phoneNumber, profileId, *, password=None):
        """Create account details; only trusted setup code supplies a password."""
        if cls.userAccountExists(username):
            return False
        account = cls(account_id=cls.generateAccountId(profileId), username=username,
            full_name=fullName, email=email, phone_number=phoneNumber, profile_id=profileId, status='Active')
        if password is not None:
            account.set_password(password)
        try:
            db.session.add(account)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    @classmethod
    def searchUserAccounts(cls, keyword=''):
        query = keyword.strip()
        statement = db.select(cls)
        if query:
            statement = statement.where(db.or_(cls.account_id.icontains(query, autoescape=True),
                cls.username.icontains(query, autoescape=True), cls.full_name.icontains(query, autoescape=True)))
        return db.session.execute(statement.order_by(cls.username, cls.account_id)).scalars().all()

    @classmethod
    def _protect_administration(cls, account_id=None, new_profile=None, profile_id=None,
                                permissions=None, status=None, profile_name=None):
        """Serialize admin mutations on the User Admin profile, preventing last-admin lockout."""
        from entity.user_profile import UserProfile
        db.session.execute(db.select(UserProfile).where(db.func.lower(UserProfile.name) == 'user admin')
                           .with_for_update().execution_options(populate_existing=True)).scalars().all()
        accounts = db.session.execute(db.select(cls).where(cls.status == 'Active')
            .execution_options(populate_existing=True)).scalars().all()
        before = after = 0
        for account in accounts:
            current = account.profile
            full_admin = account.has_password and account.active and account.is_admin and ADMIN_PERMISSIONS.issubset(set(current.permissions or []))
            before += int(full_admin)
            role, role_name, role_status, role_permissions = current, current.name, current.status, current.permissions
            account_status = account.status
            if account.account_id == account_id:
                account_status = status if status is not None else account.status
                if new_profile is not None:
                    role = new_profile
                    role_name, role_status, role_permissions = role.name, role.status, role.permissions
            if role.profile_id == profile_id:
                role_name = profile_name if profile_name is not None else role.name
                role_status = status if status is not None else role.status
                role_permissions = permissions if permissions is not None else role.permissions
            after += int(account.has_password and account_status == 'Active' and role_status == 'Active' and role_name.strip().casefold() == 'user admin'
                         and ADMIN_PERMISSIONS.issubset(set(role_permissions or [])))
        if before and not after:
            raise DomainError('Keep at least one active User Admin with all account and profile permissions.')

    @classmethod
    def updateUserAccount(cls, accountId, fullName, email, profileId):
        from entity.user_profile import UserProfile
        cls._protect_administration()  # Acquire the common admin lock before any role locks.
        account = db.session.execute(db.select(cls).where(cls.account_id == accountId)
            .with_for_update().execution_options(populate_existing=True)).scalar_one_or_none()
        if account is None:
            return False
        profile = db.session.execute(db.select(UserProfile).where(UserProfile.profile_id == profileId)
                                     .with_for_update()).scalar_one_or_none()
        if profile is None or profile.status != 'Active':
            raise DomainError('Assign an active user profile.')
        cls._protect_administration(account_id=accountId, new_profile=profile)
        changed_role = account.profile_id != profileId
        account.full_name, account.email, account.profile_id = fullName, email, profileId
        if changed_role:
            account.auth_version += 1
        try:
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    @classmethod
    def suspendUserAccount(cls, accountId):
        cls._protect_administration(account_id=accountId, status='Suspended')
        account = db.session.execute(db.select(cls).where(cls.account_id == accountId)
            .with_for_update().execution_options(populate_existing=True)).scalar_one_or_none()
        if account is None:
            return False
        if account.status == 'Suspended':
            raise DomainError('This account is already suspended')
        account.status = 'Suspended'
        account.auth_version += 1
        db.session.commit()
        return True

    @classmethod
    def login(cls, username, password):
        account = cls.getByUsername(username)
        password_ok = account.check_password(password) if account else check_password_hash(_DUMMY_HASH, password)
        return bool(account and password_ok and account.active and account.is_admin)
