from entity.validation import validate_profile_fields, valid_profile_id, search_text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from infrastructure.database import db
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

    @property
    def profileName(self):
        return self.name

    @classmethod
    def userProfileExists(cls, profileName: str) -> bool:
        return cls._profile_exists(profileName)

    @classmethod
    def _profile_exists(cls, profileName, exclude_id=None):
        statement = db.select(cls.profile_id).where(db.func.lower(cls.name) == profileName.lower())
        if exclude_id is not None:
            statement = statement.where(cls.profile_id != exclude_id)
        return db.session.execute(statement.limit(1)).first() is not None

    def _reject(self, message, field_errors=None, reason='invalid_data') -> bool:
        self.error_message = message
        self.field_errors = field_errors or {}
        self.error_reason = reason
        return False

    def createUserProfile(self, profileName: str, description: str, status: str,
                          permissions: list[str]) -> bool:
        """Validate profile data, check duplicates, and save."""
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        values, errors = validate_profile_fields(profileName, description, status, permissions)
        if errors:
            return self._reject('Please correct the errors below.', errors)
        profileName, description, status, permissions = values
        duplicate_message = 'A profile with this name already exists.'
        try:
            if self.userProfileExists(profileName):
                self.error_message = duplicate_message
                self.field_errors = {'profileName': [duplicate_message]}
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
            return False
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @classmethod
    def getUserProfile(cls, profileId: int) -> 'UserProfile | None':
        """Validate the identifier and look up a profile."""
        if not valid_profile_id(profileId):
            return None
        return db.session.get(cls, profileId)

    @classmethod
    def getProfile(cls, profilename):
        return db.session.execute(db.select(cls).where(
            db.func.lower(cls.name) == profilename.lower())).scalar_one_or_none()

    viewUserProfile = getProfile

    @classmethod
    def listUserProfiles(cls):
        return db.session.execute(db.select(cls).order_by(cls.name, cls.profile_id)).scalars().all()

    @classmethod
    def searchUserProfiles(cls, keyword: str) -> list['UserProfile']:
        keyword = search_text(keyword, required=True)
        return db.session.execute(db.select(cls).where(db.or_(
            cls.name.icontains(keyword, autoescape=True),
            cls.description.icontains(keyword, autoescape=True)
        )).order_by(cls.name)).scalars().all()

    def updateUserProfile(self, profileId: int, profileName: str, description: str,
                          permissions: list[str]) -> bool:
        """Check saved data and duplicates; preserve the stored status."""
        if not valid_profile_id(profileId):
            return self._reject('User profile not found.', reason='not_found')
        values, errors = validate_profile_fields(profileName, description, 'Active', permissions)
        if errors:
            return self._reject('Please correct the errors below.', errors)
        profileName, description, _, permissions = values
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        name = profileName
        duplicate_message = 'A profile with this name already exists.'
        try:
            profile = db.session.execute(db.select(UserProfile).where(UserProfile.profile_id == profileId)
                .with_for_update().execution_options(populate_existing=True)).scalar_one_or_none()
            if profile is None:
                db.session.rollback()
                return self._reject('User profile not found.', reason='not_found')
            if self._profile_exists(name, profileId):
                db.session.rollback()
                return self._reject(duplicate_message, {'profileName': [duplicate_message]})
            profile.name, profile.description = name, description
            profile.permissions = permissions
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return self._reject(duplicate_message, {'profileName': [duplicate_message]})
        except SQLAlchemyError:
            db.session.rollback()
            raise

    def suspendUserProfile(self, profileId: int) -> bool:
        """Suspend only existing profiles with no accounts assigned."""
        if not valid_profile_id(profileId):
            return self._reject('User profile not found.', reason='not_found')
        from infrastructure.profile_assignments import profile_account_count
        self.error_message, self.field_errors, self.error_reason = None, {}, None
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

    @classmethod
    def activeProfiles(cls):
        return db.session.scalars(db.select(cls).where(cls.status == 'Active')
            .order_by(cls.name, cls.profile_id)).all()
