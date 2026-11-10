# infrastructure/validation.py: pure value checks for direct entity calls.
from infrastructure.validation import validate_company_fields, search_text, valid_account_id
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
# infrastructure/database.py: shared SQLAlchemy database session.
from infrastructure.database import db
# entity/accounts/user_account.py: saved account lookups.
from entity.accounts.user_account import UserAccount


class CompanyProfile(db.Model):
    __tablename__ = 'company_profile'

    account_id = db.Column(db.String(32), db.ForeignKey('user_account.account_id', ondelete='RESTRICT'), primary_key=True)
    company_name = db.Column(db.String(150), nullable=False)
    company_contact = db.Column(db.String(40), nullable=False)
    company_address = db.Column(db.String(1000), nullable=False)
    company_email = db.Column(db.String(254), nullable=False)
    company_registration_number = db.Column(db.String(100), nullable=False)
    __table_args__ = (db.Index('uq_company_registration_lower', db.func.lower(company_registration_number), unique=True),)

    def createCompanyProfile(self, accountId: str, companyName: str, companyContact: str,
                             companyAddress: str, companyEmail: str,
                             companyRegistrationNumber: str) -> bool:
        """Check account and registration duplicates, then save the company profile."""
        values, errors = validate_company_fields(companyName, companyContact, companyAddress, companyEmail, companyRegistrationNumber)
        if errors:
            self.error_message = 'Please correct the errors below.'
            self.field_errors = errors or {}
            self.error_reason = 'invalid_data'
            return False
        companyName, companyContact, companyAddress = values['companyName'], values['companyContact'], values['companyAddress']
        companyEmail, companyRegistrationNumber = values['companyEmail'], values['companyRegistrationNumber']
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        try:
            if UserAccount.getUserAccount(accountId) is None:
                self.error_message = 'Account not found.'
                self.field_errors = {'accountId': ['Account not found.']}
                self.error_reason = 'not_found'
                return False
            if self.getCompanyProfile(accountId) is not None:
                self.error_message = 'This account already has a company profile.'
                self.field_errors = {}
                self.error_reason = 'invalid_data'
                return False
            duplicate = db.session.scalar(db.select(CompanyProfile.account_id).where(
                db.func.lower(CompanyProfile.company_registration_number) == companyRegistrationNumber.lower()).limit(1))
            if duplicate is not None:
                message = 'The business registration number is already registered.'
                self.error_message = message
                self.field_errors = {'companyRegistrationNumber': [message]}
                self.error_reason = 'invalid_data'
                return False
            self.account_id = accountId
            self.company_name, self.company_contact = companyName, companyContact
            self.company_address, self.company_email = companyAddress, companyEmail
            self.company_registration_number = companyRegistrationNumber
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            self.error_message = 'A company profile with this account or registration number already exists.'
            self.field_errors = {}
            self.error_reason = 'invalid_data'
            return False
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @classmethod
    def getCompanyProfile(cls, accountId: str) -> 'CompanyProfile | None':
        """Retrieve the company profile linked to this account."""
        if not valid_account_id(accountId):
            return None
        return db.session.get(cls, accountId)

    def updateCompanyProfile(self, accountId: str, companyName: str, companyContact: str,
                             companyAddress: str, companyEmail: str,
                             companyRegistrationNumber: str) -> bool:
        """Check the saved profile and registration number before updating its details."""
        values, errors = validate_company_fields(companyName, companyContact, companyAddress, companyEmail, companyRegistrationNumber)
        if errors:
            self.error_message = 'Please correct the errors below.'
            self.field_errors = errors or {}
            self.error_reason = 'invalid_data'
            return False
        companyName, companyContact, companyAddress = values['companyName'], values['companyContact'], values['companyAddress']
        companyEmail, companyRegistrationNumber = values['companyEmail'], values['companyRegistrationNumber']
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        try:
            profile = self.getCompanyProfile(accountId)
            if profile is None:
                self.error_message = 'Company profile not found.'
                self.field_errors = {}
                self.error_reason = 'not_found'
                return False
            duplicate = db.session.scalar(db.select(CompanyProfile.account_id).where(
                db.func.lower(CompanyProfile.company_registration_number) == companyRegistrationNumber.lower(),
                CompanyProfile.account_id != accountId).limit(1))
            if duplicate is not None:
                message = 'The business registration number is already registered.'
                self.error_message = message
                self.field_errors = {'companyRegistrationNumber': [message]}
                self.error_reason = 'invalid_data'
                return False
            profile.company_name, profile.company_contact = companyName, companyContact
            profile.company_address, profile.company_email = companyAddress, companyEmail
            profile.company_registration_number = companyRegistrationNumber
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            self.error_message = 'The business registration number is already registered.'
            self.field_errors = {}
            self.error_reason = 'invalid_data'
            return False
        except SQLAlchemyError:
            db.session.rollback()
            raise

    def deleteCompanyProfile(self, accountId: str) -> bool:
        """Delete the saved company profile and report database conflicts."""
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        try:
            profile = self.getCompanyProfile(accountId)
            if profile is None:
                self.error_message = 'Company profile not found.'
                self.field_errors = {}
                self.error_reason = 'not_found'
                return False
            db.session.delete(profile)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            self.error_message = 'This company profile is still in use.'
            self.field_errors = {}
            self.error_reason = 'invalid_data'
            return False
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @classmethod
    def searchCompanyProfile(cls, accountId: str, keyword: str) -> list[str]:
        """Return matching labelled details from the current account's company profile."""
        keyword = search_text(keyword)
        profile = cls.getCompanyProfile(accountId)
        if profile is None:
            return []
        fields = [('Company name', profile.company_name), ('Contact number', profile.company_contact),
                  ('Address', profile.company_address), ('Email', profile.company_email),
                  ('Business registration number', profile.company_registration_number)]
        return [f'{label}: {value}' for label, value in fields if keyword.casefold() in value.casefold()]
