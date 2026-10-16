from sqlalchemy.exc import IntegrityError

from sqlalchemy.dialects.postgresql import ARRAY

from infrastructure.database import db

class UserProfile(db.Model):
    __tablename__ = "user_profile"

    profile_id = db.Column(
        db.Integer,
        primary_key = True
    )

    name = db.Column(
        db.String(100),
        unique = True,
        nullable = False
    )

    description = db.Column(
        db.Text,
        nullable = False
    )

    permissions = db.Column(
        ARRAY(db.Text),
        nullable = False,
        default = list
    )

    status = db.Column(
        db.String(20),
        nullable=False
    )

    @classmethod
    def userProfileExists(cls, profileName: str) -> bool:
        statement = db.select(cls).where(
            cls.name == profileName.strip(
            )
        )

        existing_profile = db.session.execute(
            statement
        ).scalar_one_or_none()

        return existing_profile is not None

    @classmethod
    def createUserProfile(
        cls,
        profileName: str,
        description: str,
        status: str,
        permissions: list[str]
    ) -> bool:
        if cls.userProfileExists(profileName):
            return False

        profile = cls(
            name=profileName.strip(),
            description=description.strip(),
            status=status,
            permissions=list(permissions)
        )

        try:
            db.session.add(profile)
            db.session.commit()
            return True

        except IntegrityError:
            db.session.rollback()
            return False