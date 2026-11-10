# Entity-owned field and data checks from entity/validation.py.
from entity.validation import validate_profile_fields, positive_integer, search_text, required_text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
# Shared SQLAlchemy database session and model base from infrastructure/database.py.
from infrastructure.database import db
# Application validation and missing-data errors from infrastructure/errors.py.
from infrastructure.errors import DomainError


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

    @classmethod
    def userProfileExists(cls, profileName: str) -> bool:
        """Check whether another saved profile already uses this name.

        Uses entity/validation.py.
        """
        profileName = required_text(profileName, 'Profile name', 100)
        return db.session.execute(db.select(cls.profile_id).where(
            db.func.lower(cls.name) == profileName.lower()).limit(1)).first() is not None

    def createUserProfile(self, profileName: str, description: str, status: str,
                          permissions: list[str]) -> bool:
        """Check profile data and duplicate names, then save the new profile.

        Uses entity/validation.py.
        """
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        values, errors = validate_profile_fields(profileName, description, status, permissions)
        if errors:
            self.error_message = 'Please correct the errors below.'
            self.field_errors = errors or {}
            self.error_reason = 'invalid_data'
            return False
        profileName, description, status, permissions = values
        duplicate_message = 'A profile with this name already exists.'
        try:
            if self.userProfileExists(profileName):
                self.error_message = duplicate_message
                self.field_errors = {'profileName': [duplicate_message]}
                self.error_reason = 'invalid_data'
                return False
            self.name, self.description = profileName, description
            self.status, self.permissions = status, permissions
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            self.error_message = duplicate_message
            self.field_errors = {'profileName': [duplicate_message]}
            self.error_reason = 'invalid_data'
            return False
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @classmethod
    def getUserProfile(cls, profileId: int) -> 'UserProfile | None':
        """Look up a profile by ID, returning None when it cannot be found.

        Uses entity/validation.py.
        """
        profileId = positive_integer(profileId, 'Profile ID')
        return db.session.get(cls, profileId)

    @classmethod
    def getProfile(cls, profilename):
        """Find a role by name for trusted account setup and existing callers."""
        return db.session.execute(db.select(cls).where(
            db.func.lower(cls.name) == profilename.lower())).scalar_one_or_none()

    @classmethod
    def searchUserProfiles(cls, keyword: str) -> list['UserProfile']:
        """Validate required search text and find matching names or descriptions.

        Uses entity/validation.py.
        """
        keyword = search_text(keyword, required=True)
        return db.session.execute(db.select(cls).where(db.or_(
            cls.name.icontains(keyword, autoescape=True),
            cls.description.icontains(keyword, autoescape=True)
        )).order_by(cls.name, cls.profile_id)).scalars().all()

    @classmethod
    def listUserProfiles(cls) -> list['UserProfile']:
        """Read the alphabetical directory for initial lists and profile choices."""
        return db.session.scalars(db.select(cls).order_by(cls.name, cls.profile_id)).all()

    def updateUserProfile(self, profileId: int, profileName: str, description: str,
                          permissions: list[str]) -> bool:
        """Check saved data and duplicate names, then update fields while preserving status.

        Uses entity/validation.py.
        """
        try:
            profileId = positive_integer(profileId, 'Profile ID')
        except DomainError as error:
            self.error_message = str(error)
            self.field_errors = {'profileId': [str(error)]}
            self.error_reason = 'invalid_data'
            return False
        values, errors = validate_profile_fields(profileName, description, 'Active', permissions)
        if errors:
            self.error_message = 'Please correct the errors below.'
            self.field_errors = errors or {}
            self.error_reason = 'invalid_data'
            return False
        profileName, description, _, permissions = values
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        duplicate_message = 'A profile with this name already exists.'
        try:
            profile = db.session.execute(db.select(UserProfile).where(UserProfile.profile_id == profileId)
                .with_for_update().execution_options(populate_existing=True)).scalar_one_or_none()
            if profile is None:
                db.session.rollback()
                self.error_message = 'User profile not found.'
                self.field_errors = {}
                self.error_reason = 'not_found'
                return False
            if profile.name.lower() != profileName.lower() and self.userProfileExists(profileName):
                db.session.rollback()
                self.error_message = duplicate_message
                self.field_errors = {'profileName': [duplicate_message]}
                self.error_reason = 'invalid_data'
                return False
            profile.name, profile.description = profileName, description
            profile.permissions = permissions
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            self.error_message = duplicate_message
            self.field_errors = {'profileName': [duplicate_message]}
            self.error_reason = 'invalid_data'
            return False
        except SQLAlchemyError:
            db.session.rollback()
            raise

    def suspendUserProfile(self, profileId: int) -> bool:
        """Suspend a saved profile only when no account is assigned to it.

        Uses entity/validation.py.
        """
        try:
            profileId = positive_integer(profileId, 'Profile ID')
        except DomainError as error:
            self.error_message = str(error)
            self.field_errors = {'profileId': [str(error)]}
            self.error_reason = 'invalid_data'
            return False
        # Entity used for saved data or return-value types from entity/accounts/user_account.py.
        from entity.accounts.user_account import UserAccount
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        try:
            profile = db.session.execute(db.select(UserProfile).where(UserProfile.profile_id == profileId)
                .with_for_update().execution_options(populate_existing=True)).scalar_one_or_none()
            if profile is None:
                db.session.rollback()
                self.error_message = 'User profile not found.'
                self.field_errors = {}
                self.error_reason = 'not_found'
                return False
            assigned_accounts = db.session.scalar(db.select(db.func.count()).select_from(UserAccount)
                .where(UserAccount.profile_id == profileId))
            if assigned_accounts:
                raise DomainError('This profile is in use.')
            profile.status = 'Suspended'
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
