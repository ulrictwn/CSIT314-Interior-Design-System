from entity.validation import (validate_account_fields, validate_account_details,
    validate_login_credentials, valid_account_id, search_text, password_value, required_text, positive_integer)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
from infrastructure.database import db
from infrastructure.errors import DomainError
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
        return self.status == 'Active' and self.profile.status == 'Active'

    @property
    def has_password(self):
        return bool(self.password_hash and self.password_hash != _UNSET_PASSWORD_HASH)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password_value(password))

    def check_password(self, password):
        return self.has_password and check_password_hash(self.password_hash, password)

    @classmethod
    def userAccountExists(cls, username: str) -> bool:
        username = required_text(username, 'Username', 80)
        return db.session.execute(db.select(cls.account_id).where(
            db.func.lower(cls.username) == username.lower()).limit(1)).first() is not None

    @classmethod
    def getByUsername(cls, username):
        return db.session.execute(db.select(cls).where(
            db.func.lower(cls.username) == username.lower())).scalar_one_or_none()

    @classmethod
    def getUserAccount(cls, accountId: str) -> 'UserAccount | None':
        if not valid_account_id(accountId):
            return None
        return db.session.get(cls, accountId)

    def _reject(self, message, field_errors=None, reason='invalid_data') -> bool:
        self.error_message = message
        self.field_errors = field_errors or {}
        self.error_reason = reason
        return False

    @classmethod
    def _email_exists(cls, email, exclude_id=None):
        statement = db.select(cls.account_id).where(db.func.lower(cls.email) == email.lower())
        if exclude_id is not None:
            statement = statement.where(cls.account_id != exclude_id)
        return db.session.execute(statement.limit(1)).first() is not None

    @classmethod
    def generateAccountId(cls, profileId: int) -> str:
        """Combine the profile's actual ID with a shared, minimum-two-digit number.

        The counter is locked until the account creation transaction commits.
        Existing accounts keep their IDs; legacy per-role counters are ignored.
        """
        profileId = positive_integer(profileId, 'Profile ID')
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
        """Create an account with the default password unless trusted setup supplies one."""
        values, errors = validate_account_fields(username, fullName, email, phoneNumber, profileId)
        if errors:
            return self._reject('Please correct the errors below.', errors)
        username, fullName, email = values['username'], values['full_name'], values['email']
        phoneNumber, profileId = values['phone_number'], values['profile_id']
        if password != _DEFAULT_ACCOUNT_PASSWORD:
            try:
                password_value(password)
            except DomainError as error:
                return self._reject(str(error), {'password': [str(error)]})
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        try:
            if self.userAccountExists(username):
                db.session.rollback()
                message = 'The username is already registered.'
                return self._reject(message, {'username': [message]})
            if self._email_exists(email):
                db.session.rollback()
                message = 'The email is already registered.'
                return self._reject(message, {'email': [message]})
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
            return self._reject(str(error), {'profile_id': [str(error)]})
        except IntegrityError:
            db.session.rollback()
            return self._reject('The username or email is already registered.')
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @classmethod
    def searchUserAccounts(cls, keyword: str = '') -> list['UserAccount']:
        keyword = search_text(keyword)
        query = keyword
        statement = db.select(cls)
        if query:
            statement = statement.where(db.or_(cls.account_id.icontains(query, autoescape=True),
                cls.username.icontains(query, autoescape=True), cls.full_name.icontains(query, autoescape=True)))
        return db.session.execute(statement.order_by(cls.username, cls.account_id)).scalars().all()

    def updateUserAccount(self, accountId: str, fullName: str, email: str, profileId: int) -> bool:
        if not valid_account_id(accountId):
            return self._reject('User account not found.', reason='not_found')
        values, errors = validate_account_details(fullName, email, profileId)
        if errors:
            return self._reject('Please correct the errors below.', errors)
        fullName, email, profileId = values['full_name'], values['email'], values['profile_id']
        from entity.profile.user_profile import UserProfile
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        try:
            account = db.session.execute(db.select(UserAccount).where(UserAccount.account_id == accountId)
                .with_for_update().execution_options(populate_existing=True)).scalar_one_or_none()
            if account is None:
                db.session.rollback()
                return self._reject('User account not found.', reason='not_found')
            profile = db.session.execute(db.select(UserProfile).where(UserProfile.profile_id == profileId)
                                         .with_for_update()).scalar_one_or_none()
            if profile is None or profile.status != 'Active':
                db.session.rollback()
                message = 'Assign an active user profile.'
                return self._reject(message, {'profile_id': [message]})
            if self._email_exists(email, accountId):
                db.session.rollback()
                message = 'The email is already registered.'
                return self._reject(message, {'email': [message]})
            account.full_name, account.email = fullName, email
            account.profile_id = profileId
            db.session.commit()
            return True
        except DomainError as error:
            db.session.rollback()
            return self._reject(str(error))
        except IntegrityError:
            db.session.rollback()
            message = 'The email is already registered.'
            return self._reject(message, {'email': [message]})
        except SQLAlchemyError:
            db.session.rollback()
            raise

    def suspendUserAccount(self, accountId: str) -> bool:
        if not valid_account_id(accountId):
            return self._reject('User account not found.', reason='not_found')
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        try:
            account = db.session.execute(db.select(UserAccount).where(UserAccount.account_id == accountId)
                .with_for_update().execution_options(populate_existing=True)).scalar_one_or_none()
            if account is None:
                db.session.rollback()
                return self._reject('User account not found.', reason='not_found')
            if account.status == 'Suspended':
                db.session.rollback()
                return self._reject('This account is already suspended')
            account.status = 'Suspended'
            db.session.commit()
            return True
        except DomainError as error:
            db.session.rollback()
            return self._reject(str(error))
        except SQLAlchemyError:
            db.session.rollback()
            raise

    def login(self, username: str, password: str, profileName: str = 'User Admin') -> bool:
        self.authenticated_account = None
        try:
            username = validate_login_credentials(username, password)
        except DomainError as error:
            return self._reject(str(error), error.field_errors)
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        self.authenticated_account = None
        account = self.getByUsername(username)
        roles = {profileName.casefold()}
        if profileName.casefold() in ('platform manager', 'platform management'):
            roles = {'platform manager', 'platform management'}
        if not (account and account.check_password(password) and account.active
                and account.profile.name.casefold() in roles):
            return self._reject('Invalid login details')
        self.authenticated_account = account
        from entity.reports.activity_event import ActivityEvent
        ActivityEvent.record('login_success', account.account_id)
        db.session.commit()
        return True

    def portalRole(self):
        """Resolve the portal from the saved active account and profile."""
        if not self.active:
            return None
        return {'user admin': 'admin', 'interior designer': 'designer',
                'customer': 'customer', 'platform manager': 'manager',
                'platform management': 'manager'}.get(self.profile.name.casefold())

    @staticmethod
    def staffRole(role):
        if not isinstance(role, str) or role not in ('admin', 'designer', 'manager'):
            error = DomainError('Choose a supported staff role.')
            error.field_errors = {'staffRole': [str(error)]}
            raise error
        return role
