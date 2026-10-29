import re
from email_validator import validate_email, EmailNotValidError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
from infrastructure.database import db
from entity.auth.login_attempt import LoginAttempt
from infrastructure.errors import DomainError
from infrastructure.permissions import ADMIN_PERMISSIONS
from infrastructure.time import utcnow

_DUMMY_HASH = generate_password_hash('not-an-actual-account-password')
_UNSET_PASSWORD_HASH = '!'
_GLOBAL_ACCOUNT_COUNTER = '*'


def required_text(value, label, maximum=10000):
    if not isinstance(value, str) or not value.strip():
        raise DomainError(f'{label} is required.')
    value = value.strip()
    if len(value) > maximum:
        raise DomainError(f'{label} must be at most {maximum} characters.')
    return value


def username_value(value):
    value = required_text(value, 'Username', 80)
    if not re.fullmatch(r'[A-Za-z0-9_.-]{3,80}', value):
        raise DomainError('Username must contain 3–80 letters, numbers, dots, underscores, or hyphens.')
    return value


def email_address(value):
    try:
        return validate_email(required_text(value, 'Email', 254), check_deliverability=False).normalized.lower()
    except EmailNotValidError as error:
        raise DomainError('Enter a valid email address.') from error


def phone_number_value(value):
    value = required_text(value, 'Phone number', 40)
    if not re.fullmatch(r'\+?[0-9][0-9 ()-]{5,38}', value):
        raise DomainError('Enter a valid phone number.')
    return value


def password_value(value):
    if not isinstance(value, str) or not 12 <= len(value) <= 128:
        raise DomainError('Passwords must contain between 12 and 128 characters.')
    return value


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
    def userAccountExists(cls, username: str) -> bool:
        if not isinstance(username, str) or not username.strip():
            return False
        return db.session.execute(db.select(cls.account_id).where(
            db.func.lower(cls.username) == username.strip().lower()).limit(1)).first() is not None

    @classmethod
    def getByUsername(cls, username):
        if not isinstance(username, str) or not username.strip():
            return None
        return db.session.execute(db.select(cls).where(
            db.func.lower(cls.username) == username.strip().lower())).scalar_one_or_none()

    @classmethod
    def getUserAccount(cls, accountId: str) -> 'UserAccount | None':
        if not cls._valid_account_id(accountId):
            return None
        return db.session.get(cls, accountId)

    @staticmethod
    def _valid_account_id(accountId):
        return isinstance(accountId, str) and bool(accountId.strip()) and len(accountId) <= 32

    @staticmethod
    def _validate_details(fullName, email, profileId):
        values, errors = {}, {}
        for field, validator in {
            'full_name': lambda: required_text(fullName, 'Full name', 120),
            'email': lambda: email_address(email),
        }.items():
            try:
                values[field] = validator()
            except DomainError as error:
                errors[field] = [str(error)]
        if type(profileId) is not int or not 1 <= profileId <= 2_147_483_647:
            errors['profile_id'] = ['Assign an active user profile.']
        return values, errors

    def _reject(self, message, field_errors=None, reason='invalid_data') -> bool:
        self.error_message = message
        self.field_errors = field_errors or {}
        self.error_reason = reason
        return False

    @classmethod
    def activeProfiles(cls):
        from entity.profile.user_profile import UserProfile
        return db.session.execute(db.select(UserProfile).where(UserProfile.status == 'Active')
            .order_by(UserProfile.name, UserProfile.profile_id)).scalars().all()

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
        from entity.profile.user_profile import UserProfile
        if not UserProfile._valid_profile_id(profileId):
            raise DomainError('Assign an active user profile.')
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

    def createUserAccount(self, username: str, fullName: str, email: str,
                          phoneNumber: str, profileId: int, *, password=None) -> bool:
        """Validate and save account data; only trusted setup can supply a password."""
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        values, errors = self._validate_details(fullName, email, profileId)
        for field, validator in {
            'username': lambda: username_value(username),
            'phone_number': lambda: phone_number_value(phoneNumber),
        }.items():
            try:
                values[field] = validator()
            except DomainError as error:
                errors[field] = [str(error)]
        if password is not None:
            try:
                password_value(password)
            except DomainError as error:
                errors['password'] = [str(error)]
        if errors:
            return self._reject('Please correct the errors below.', errors)
        try:
            if self.userAccountExists(values['username']):
                db.session.rollback()
                message = 'The username is already registered.'
                return self._reject(message, {'username': [message]})
            if self._email_exists(values['email']):
                db.session.rollback()
                message = 'The email is already registered.'
                return self._reject(message, {'email': [message]})
            self.account_id = self.generateAccountId(profileId)
            self.username, self.full_name = values['username'], values['full_name']
            self.email, self.phone_number = values['email'], values['phone_number']
            self.profile_id, self.status = profileId, 'Active'
            self.password_hash = _UNSET_PASSWORD_HASH
            if password is not None:
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
        if not isinstance(keyword, str) or len(keyword) > 200:
            raise DomainError('Search text must contain at most 200 characters.')
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
        from entity.profile.user_profile import UserProfile
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

    def updateUserAccount(self, accountId: str, fullName: str, email: str, profileId: int) -> bool:
        from entity.profile.user_profile import UserProfile
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        if not self._valid_account_id(accountId):
            return self._reject('User account not found.', reason='not_found')
        values, errors = self._validate_details(fullName, email, profileId)
        if errors:
            return self._reject('Please correct the errors below.', errors)
        try:
            self._protect_administration()  # Acquire the common admin lock before role locks.
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
            if self._email_exists(values['email'], accountId):
                db.session.rollback()
                message = 'The email is already registered.'
                return self._reject(message, {'email': [message]})
            self._protect_administration(account_id=accountId, new_profile=profile)
            changed_role = account.profile_id != profileId
            account.full_name, account.email = values['full_name'], values['email']
            account.profile_id = profileId
            if changed_role:
                account.auth_version += 1
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
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        if not self._valid_account_id(accountId):
            return self._reject('User account not found.', reason='not_found')
        try:
            self._protect_administration(account_id=accountId, status='Suspended')
            account = db.session.execute(db.select(UserAccount).where(UserAccount.account_id == accountId)
                .with_for_update().execution_options(populate_existing=True)).scalar_one_or_none()
            if account is None:
                db.session.rollback()
                return self._reject('User account not found.', reason='not_found')
            if account.status == 'Suspended':
                db.session.rollback()
                return self._reject('This account is already suspended')
            account.status = 'Suspended'
            account.auth_version += 1
            db.session.commit()
            return True
        except DomainError as error:
            db.session.rollback()
            return self._reject(str(error))
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @staticmethod
    def validateLoginCredentials(username: str, password: str) -> str:
        """Apply the existing required-field and length rules before database access."""
        errors = {}
        for field, value, maximum in [('username', username, 80), ('password', password, 128)]:
            if not isinstance(value, str) or not value.strip():
                errors[field] = ['This field is required.']
            elif len(value) > maximum:
                errors[field] = [f'Field cannot be longer than {maximum} characters.']
        if errors:
            error = DomainError('Invalid login details')
            error.field_errors = errors
            raise error
        return username.strip()

    def login(self, username: str, password: str, *, remote_address: str = '',
              attempt_limit: int = 5) -> bool:
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        self.authenticated_account = None
        try:
            username = self.validateLoginCredentials(username, password)
        except DomainError as error:
            return self._reject(str(error), error.field_errors)
        key = LoginAttempt.keyFor(username, remote_address)
        if LoginAttempt.isLimited(key, attempt_limit):
            return self._reject('Too many unsuccessful attempts. Try again in 15 minutes.')
        account = self.getByUsername(username)
        password_ok = account.check_password(password) if account else check_password_hash(_DUMMY_HASH, password)
        if not (account and password_ok and account.active and account.is_admin):
            LoginAttempt.recordFailure(key)
            return self._reject('Invalid login details')
        LoginAttempt.clearFailures(key)
        self.authenticated_account = account
        return True
