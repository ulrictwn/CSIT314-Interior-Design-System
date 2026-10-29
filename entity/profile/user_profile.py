from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from infrastructure.database import db
from infrastructure.errors import DomainError
from infrastructure.permissions import PERMISSION_OPTIONS


class UserProfile(db.Model):
    __tablename__ = 'user_profile'

    profile_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    permissions = db.Column(
        MutableList.as_mutable(db.JSON().with_variant(ARRAY(db.Text), 'postgresql')),
        nullable=False, default=list)
    __table_args__ = (db.Index('uq_profile_name_lower', db.func.lower(name), unique=True),)

    @property
    def profileName(self):
        return self.name

    @classmethod
    def userProfileExists(cls, profileName: str, exclude_id=None) -> bool:
        if not isinstance(profileName, str) or not profileName.strip():
            return False
        statement = db.select(cls.profile_id).where(db.func.lower(cls.name) == profileName.strip().lower())
        if exclude_id is not None:
            statement = statement.where(cls.profile_id != exclude_id)
        return db.session.execute(statement.limit(1)).first() is not None

    @staticmethod
    def _validate_profile_fields(profileName, description, status, permissions):
        """Collect field errors and normalize data without database access."""
        errors = {}
        values = []
        for field, value, label, maximum in (
                ('profileName', profileName, 'Profile name', 100),
                ('description', description, 'Description', 10000)):
            if not isinstance(value, str) or not value.strip():
                errors[field] = [f'{label} is required.']
            elif len(value.strip()) > maximum:
                errors[field] = [f'{label} must be at most {maximum} characters.']
            values.append(value.strip() if isinstance(value, str) else value)
        if not isinstance(status, bool):
            errors['status'] = ['Choose Active or Suspended.']
        if not isinstance(permissions, list) or any(
                not isinstance(p, str) or p not in PERMISSION_OPTIONS for p in permissions):
            errors['permissions'] = ['Choose permissions from the supported list.']
        if errors:
            return None, errors
        return (values[0], values[1], 'Active' if status else 'Suspended',
                list(dict.fromkeys(permissions))), {}

    @staticmethod
    def _valid_profile_id(profileId):
        return type(profileId) is int and 1 <= profileId <= 2_147_483_647

    def _reject(self, message, field_errors=None, reason='invalid_data') -> bool:
        self.error_message = message
        self.field_errors = field_errors or {}
        self.error_reason = reason
        return False

    def createUserProfile(self, profileName: str, description: str, status: bool,
                          permissions: list[str]) -> bool:
        """Validate, check uniqueness, and save; invalid profiles return False."""
        self.error_message = None
        values, self.field_errors = self._validate_profile_fields(
            profileName, description, status, permissions)
        if self.field_errors:
            self.error_message = 'Please correct the errors below.'
            return False
        profileName, description, stored_status, permissions = values
        duplicate_message = 'A profile with this name already exists.'
        try:
            if self.userProfileExists(profileName):
                self.error_message = duplicate_message
                self.field_errors = {'profileName': [duplicate_message]}
                return False
            self.name, self.description = profileName, description
            self.status, self.permissions = stored_status, permissions
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            self.error_message = duplicate_message
            self.field_errors = {'profileName': [duplicate_message]}
            return False
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @classmethod
    def getUserProfile(cls, profileId: int) -> 'UserProfile | None':
        """Validate the database integer ID before looking up a profile."""
        if not cls._valid_profile_id(profileId):
            return None
        return db.session.get(cls, profileId)

    @classmethod
    def getProfile(cls, profilename):
        return db.session.execute(db.select(cls).where(
            db.func.lower(cls.name) == profilename.strip().lower())).scalar_one_or_none()

    viewUserProfile = getProfile

    @classmethod
    def listUserProfiles(cls):
        return db.session.execute(db.select(cls).order_by(cls.name, cls.profile_id)).scalars().all()

    @classmethod
    def searchUserProfiles(cls, keyword: str) -> list['UserProfile']:
        if not isinstance(keyword, str) or not keyword.strip():
            raise DomainError('Search text is required.')
        query = keyword.strip()
        if len(query) > 200:
            raise DomainError('Search text must be at most 200 characters.')
        return db.session.execute(db.select(cls).where(db.or_(
            cls.name.icontains(query, autoescape=True),
            cls.description.icontains(query, autoescape=True)
        )).order_by(cls.name)).scalars().all()

    def updateUserProfile(self, profileId: int, profileName: str, description: str,
                          permissions: list[str], status: bool | None = None) -> bool:
        """Validate profile edits and save; omitted status keeps the stored value."""
        from infrastructure.profile_assignments import profile_account_count
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        if not self._valid_profile_id(profileId):
            return self._reject('User profile not found.', reason='not_found')
        values, errors = self._validate_profile_fields(
            profileName, description, True if status is None else status, permissions)
        if errors:
            return self._reject('Please correct the errors below.', errors)
        name, description, normalized_status, permissions = values
        duplicate_message = 'A profile with this name already exists.'
        try:
            profile = db.session.execute(db.select(UserProfile).where(UserProfile.profile_id == profileId)
                .with_for_update().execution_options(populate_existing=True)).scalar_one_or_none()
            if profile is None:
                db.session.rollback()
                return self._reject('User profile not found.', reason='not_found')
            if self.userProfileExists(name, profileId):
                db.session.rollback()
                return self._reject(duplicate_message, {'profileName': [duplicate_message]})
            new_status = profile.status if status is None else normalized_status
            if new_status != 'Active' and profile_account_count(profileId):
                raise DomainError('This profile is in use.')
            if profile.name.strip().casefold() == 'user admin':
                from entity.accounts.user_account import UserAccount
                UserAccount._protect_administration(profile_id=profileId, profile_name=name,
                    permissions=permissions, status=new_status)
            profile.name, profile.description = name, description
            profile.status, profile.permissions = new_status, permissions
            db.session.commit()
            return True
        except DomainError as error:
            db.session.rollback()
            return self._reject(str(error))
        except IntegrityError:
            db.session.rollback()
            return self._reject(duplicate_message, {'profileName': [duplicate_message]})
        except SQLAlchemyError:
            db.session.rollback()
            raise

    def suspendUserProfile(self, profileId: int) -> bool:
        """Suspend only existing profiles with no accounts assigned."""
        from infrastructure.profile_assignments import profile_account_count
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        if not self._valid_profile_id(profileId):
            return self._reject('User profile not found.', reason='not_found')
        try:
            profile = db.session.execute(db.select(UserProfile).where(UserProfile.profile_id == profileId)
                .with_for_update().execution_options(populate_existing=True)).scalar_one_or_none()
            if profile is None:
                db.session.rollback()
                return self._reject('User profile not found.', reason='not_found')
            if profile_account_count(profileId):
                raise DomainError('This profile is in use.')
            profile.status = 'Suspended'
            db.session.commit()
            return True
        except DomainError as error:
            db.session.rollback()
            return self._reject(str(error))
        except SQLAlchemyError:
            db.session.rollback()
            raise
