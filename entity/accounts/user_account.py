# Entity-owned field and data checks from entity/validation.py.
from entity.validation import (validate_account_fields, validate_account_details,
    validate_login_credentials, valid_account_id, search_text, password_value, required_text, positive_integer)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
# Shared SQLAlchemy database session and model base from infrastructure/database.py.
from infrastructure.database import db
# Application validation and missing-data errors from infrastructure/errors.py.
from infrastructure.errors import DomainError
# UTC timestamps for saved account data from infrastructure/time.py.
from infrastructure.time import utcnow

_UNSET_PASSWORD_HASH = '!'
_DEFAULT_ACCOUNT_PASSWORD = 'password'
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
    # Retained for compatibility with existing databases; unused by the demo.
    auth_version = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    profile = db.relationship('UserProfile')
    __table_args__ = (
        db.Index('uq_account_username_lower', db.func.lower(username), unique=True),
        db.Index('uq_account_email_lower', db.func.lower(email), unique=True),
    )

    @property
    def active(self):
        """Report whether both the account and its assigned profile are active."""
        return self.status == 'Active' and self.profile.status == 'Active'

    @property
    def has_password(self):
        """Report whether a saved password hash is available for login."""
        return bool(self.password_hash and self.password_hash != _UNSET_PASSWORD_HASH)

    def set_password(self, password):
        """Validate and hash a private password for trusted setup or reset commands.

        Uses entity/validation.py.
        """
        self.password_hash = generate_password_hash(password_value(password))

    def check_password(self, password):
        """Compare the submitted password with the saved hash."""
        return self.has_password and check_password_hash(self.password_hash, password)

    @classmethod
    def userAccountExists(cls, username: str) -> bool:
        """Check whether a saved account already uses this username.

        Uses entity/validation.py.
        """
        username = required_text(username, 'Username', 80)
        return db.session.execute(db.select(cls.account_id).where(
            db.func.lower(cls.username) == username.lower()).limit(1)).first() is not None

    @classmethod
    def getByUsername(cls, username):
        """Find an account by username for login and trusted setup commands."""
        return db.session.execute(db.select(cls).where(
            db.func.lower(cls.username) == username.lower())).scalar_one_or_none()

    @classmethod
    def getUserAccount(cls, accountId: str) -> 'UserAccount | None':
        """Look up an account by ID, returning None for missing or invalid IDs.

        Uses entity/validation.py.
        """
        if not valid_account_id(accountId):
            return None
        return db.session.get(cls, accountId)

    @classmethod
    def generateAccountId(cls, profileId: int) -> str:
        """Generate an unused ID from the selected profile and shared account counter.

        Uses entity/validation.py.
        """
        profileId = positive_integer(profileId, 'Profile ID')
        # Entity used for saved data or return-value types from entity/profile/user_profile.py.
        from entity.profile.user_profile import UserProfile
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

    def createUserAccount(self, username: str, password: str, fullName: str, email: str,
                          phoneNumber: str, profileId: int) -> bool:
        """Check account data and duplicates, generate its ID and save a password hash.

        Uses entity/validation.py.
        """
        values, errors = validate_account_fields(username, fullName, email, phoneNumber, profileId)
        if errors:
            self.error_message = 'Please correct the errors below.'
            self.field_errors = errors or {}
            self.error_reason = 'invalid_data'
            return False
        username, fullName, email = values['username'], values['full_name'], values['email']
        phoneNumber, profileId = values['phone_number'], values['profile_id']
        if password != _DEFAULT_ACCOUNT_PASSWORD:
            try:
                password_value(password)
            except DomainError as error:
                self.error_message = str(error)
                self.field_errors = {'password': [str(error)]}
                self.error_reason = 'invalid_data'
                return False
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        try:
            if self.userAccountExists(username):
                db.session.rollback()
                message = 'The username is already registered.'
                self.error_message = message
                self.field_errors = {'username': [message]}
                self.error_reason = 'invalid_data'
                return False
            duplicate_email = db.session.execute(db.select(UserAccount.account_id).where(
                db.func.lower(UserAccount.email) == email.lower()).limit(1)).first()
            if duplicate_email is not None:
                db.session.rollback()
                message = 'The email is already registered.'
                self.error_message = message
                self.field_errors = {'email': [message]}
                self.error_reason = 'invalid_data'
                return False
            self.account_id = self.generateAccountId(profileId)
            self.username, self.full_name = username, fullName
            self.email, self.phone_number = email, phoneNumber
            self.profile_id, self.status = profileId, 'Active'
            if password == _DEFAULT_ACCOUNT_PASSWORD:
                self.password_hash = generate_password_hash(_DEFAULT_ACCOUNT_PASSWORD)
            else:
                self.set_password(password)
            db.session.add(self)
            db.session.commit()
            return True
        except DomainError as error:
            db.session.rollback()
            self.error_message = str(error)
            self.field_errors = {'profile_id': [str(error)]}
            self.error_reason = 'invalid_data'
            return False
        except IntegrityError:
            db.session.rollback()
            self.error_message = 'The username or email is already registered.'
            self.field_errors = {}
            self.error_reason = 'invalid_data'
            return False
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @classmethod
    def searchUserAccounts(cls, keyword: str = '') -> list['UserAccount']:
        """Find accounts by ID, username or full name; blank lists all accounts.

        Uses entity/validation.py.
        """
        keyword = search_text(keyword)
        statement = db.select(cls)
        if keyword:
            statement = statement.where(db.or_(cls.account_id.icontains(keyword, autoescape=True),
                cls.username.icontains(keyword, autoescape=True), cls.full_name.icontains(keyword, autoescape=True)))
        return db.session.execute(statement.order_by(cls.username, cls.account_id)).scalars().all()

    def updateUserAccount(self, accountId: str, fullName: str, email: str, profileId: int) -> bool:
        """Check the saved account, active profile and duplicate email before updating.

        Uses entity/validation.py.
        """
        if not valid_account_id(accountId):
            self.error_message = 'User account not found.'
            self.field_errors = {}
            self.error_reason = 'not_found'
            return False
        values, errors = validate_account_details(fullName, email, profileId)
        if errors:
            self.error_message = 'Please correct the errors below.'
            self.field_errors = errors or {}
            self.error_reason = 'invalid_data'
            return False
        fullName, email, profileId = values['full_name'], values['email'], values['profile_id']
        # Entity used for saved data or return-value types from entity/profile/user_profile.py.
        from entity.profile.user_profile import UserProfile
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        try:
            account = db.session.execute(db.select(UserAccount).where(UserAccount.account_id == accountId)
                .with_for_update().execution_options(populate_existing=True)).scalar_one_or_none()
            if account is None:
                db.session.rollback()
                self.error_message = 'User account not found.'
                self.field_errors = {}
                self.error_reason = 'not_found'
                return False
            profile = db.session.execute(db.select(UserProfile).where(UserProfile.profile_id == profileId)
                                         .with_for_update()).scalar_one_or_none()
            if profile is None or profile.status != 'Active':
                db.session.rollback()
                message = 'Assign an active user profile.'
                self.error_message = message
                self.field_errors = {'profile_id': [message]}
                self.error_reason = 'invalid_data'
                return False
            duplicate_email = db.session.execute(db.select(UserAccount.account_id).where(
                db.func.lower(UserAccount.email) == email.lower(),
                UserAccount.account_id != accountId).limit(1)).first()
            if duplicate_email is not None:
                db.session.rollback()
                message = 'The email is already registered.'
                self.error_message = message
                self.field_errors = {'email': [message]}
                self.error_reason = 'invalid_data'
                return False
            account.full_name, account.email = fullName, email
            account.profile_id = profileId
            db.session.commit()
            return True
        except DomainError as error:
            db.session.rollback()
            self.error_message = str(error)
            self.field_errors = {}
            self.error_reason = 'invalid_data'
            return False
        except IntegrityError:
            db.session.rollback()
            message = 'The email is already registered.'
            self.error_message = message
            self.field_errors = {'email': [message]}
            self.error_reason = 'invalid_data'
            return False
        except SQLAlchemyError:
            db.session.rollback()
            raise

    def suspendUserAccount(self, accountId: str) -> bool:
        """Suspend an existing active account, rejecting missing or suspended accounts.

        Uses entity/validation.py.
        """
        if not valid_account_id(accountId):
            self.error_message = 'User account not found.'
            self.field_errors = {}
            self.error_reason = 'not_found'
            return False
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        try:
            account = db.session.execute(db.select(UserAccount).where(UserAccount.account_id == accountId)
                .with_for_update().execution_options(populate_existing=True)).scalar_one_or_none()
            if account is None:
                db.session.rollback()
                self.error_message = 'User account not found.'
                self.field_errors = {}
                self.error_reason = 'not_found'
                return False
            if account.status == 'Suspended':
                db.session.rollback()
                self.error_message = 'This account is already suspended'
                self.field_errors = {}
                self.error_reason = 'invalid_data'
                return False
            account.status = 'Suspended'
            db.session.commit()
            return True
        except DomainError as error:
            db.session.rollback()
            self.error_message = str(error)
            self.field_errors = {}
            self.error_reason = 'invalid_data'
            return False
        except SQLAlchemyError:
            db.session.rollback()
            raise

    def login(self, username: str, password: str, profileName: str = 'User Admin') -> bool:
        """Check saved credentials, role and status, then record a successful login.

        Uses entity/reports/activity_event.py, entity/validation.py.
        """
        self.authenticated_account = None
        try:
            username = validate_login_credentials(username, password)
        except DomainError as error:
            self.error_message = str(error)
            self.field_errors = error.field_errors or {}
            self.error_reason = 'invalid_data'
            return False
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        self.authenticated_account = None
        account = self.getByUsername(username)
        roles = {profileName.casefold()}
        if profileName.casefold() in ('platform manager', 'platform management'):
            roles = {'platform manager', 'platform management'}
        if not (account and account.check_password(password) and account.active
                and account.profile.name.casefold() in roles):
            self.error_message = 'Invalid login details'
            self.field_errors = {}
            self.error_reason = 'invalid_data'
            return False
        self.authenticated_account = account
        # Entity used for saved data or return-value types from entity/reports/activity_event.py.
        from entity.reports.activity_event import ActivityEvent
        ActivityEvent.record('login_success', account.account_id)
        db.session.commit()
        return True

    @staticmethod
    def staffRole(role):
        """Validate the staff portal choice before its controller selects a login page."""
        if not isinstance(role, str) or role not in ('admin', 'designer', 'manager'):
            error = DomainError('Choose a supported staff role.')
            error.field_errors = {'staffRole': [str(error)]}
            raise error
        return role

    def portalRole(self):
        """Resolve the active account role used by the portal session checks."""
        if not self.active:
            return None
        return {'user admin': 'admin', 'interior designer': 'designer',
                'customer': 'customer', 'platform manager': 'manager',
                'platform management': 'manager'}.get(self.profile.name.casefold())
