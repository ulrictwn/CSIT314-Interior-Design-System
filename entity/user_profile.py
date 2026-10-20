from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.exc import IntegrityError
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
    def userProfileExists(cls, profileName, exclude_id=None):
        statement = db.select(cls.profile_id).where(db.func.lower(cls.name) == profileName.strip().lower())
        if exclude_id is not None:
            statement = statement.where(cls.profile_id != exclude_id)
        return db.session.execute(statement.limit(1)).first() is not None

    @classmethod
    def createUserProfile(cls, profileName, description, status, permissions):
        if cls.userProfileExists(profileName):
            return False
        profile = cls(name=profileName.strip(), description=description.strip(), status=status,
                      permissions=list(dict.fromkeys(permissions)))
        try:
            db.session.add(profile)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    @classmethod
    def getUserProfile(cls, profileId):
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
    def searchUserProfiles(cls, keyword):
        query = keyword.strip()
        return db.session.execute(db.select(cls).where(db.or_(
            cls.name.icontains(query, autoescape=True),
            cls.description.icontains(query, autoescape=True)
        )).order_by(cls.name)).scalars().all()

    @classmethod
    def updateUserProfile(cls, profileId, profileName, description, permissions, status=None):
        from infrastructure.profile_assignments import profile_account_count
        profile = db.session.execute(db.select(cls).where(cls.profile_id == profileId)
                                     .with_for_update()).scalar_one_or_none()
        if profile is None or cls.userProfileExists(profileName, profileId):
            return False
        new_status = status if status is not None else profile.status
        if new_status != 'Active' and profile_account_count(profileId):
            raise DomainError('This profile is in use.')
        if profile.name.strip().casefold() == 'user admin':
            from entity.user_account import UserAccount
            UserAccount._protect_administration(profile_id=profileId, profile_name=profileName,
                permissions=permissions, status=new_status)
        profile.name, profile.description = profileName.strip(), description.strip()
        profile.status, profile.permissions = new_status, list(dict.fromkeys(permissions))
        try:
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False

    @classmethod
    def suspendUserProfile(cls, profileId):
        from infrastructure.profile_assignments import profile_account_count
        profile = db.session.execute(db.select(cls).where(cls.profile_id == profileId)
                                     .with_for_update()).scalar_one_or_none()
        if profile is None:
            return False
        if profile_account_count(profileId):
            raise DomainError('This profile is in use.')
        profile.status = 'Suspended'
        db.session.commit()
        return True
