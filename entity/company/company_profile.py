from entity.company.validation import validate_company_fields
from entity.validation import search_text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from infrastructure.database import db
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

    def _reject(self, message, field_errors=None, reason='invalid_data') -> bool:
        self.error_message, self.field_errors, self.error_reason = message, field_errors or {}, reason
        return False

    @classmethod
    def _registration_exists(cls, registration_number, exclude_account=None):
        statement = db.select(cls.account_id).where(
            db.func.lower(cls.company_registration_number) == registration_number.lower())
        if exclude_account is not None:
            statement = statement.where(cls.account_id != exclude_account)
        return db.session.execute(statement.limit(1)).first() is not None

    def createCompanyProfile(self, accountId: str, companyName: str, companyContact: str,
                             companyAddress: str, companyEmail: str,
                             companyRegistrationNumber: str) -> bool:
        values, errors = validate_company_fields(companyName, companyContact, companyAddress, companyEmail, companyRegistrationNumber)
        if errors:
            return self._reject('Please correct the errors below.', errors)
        companyName, companyContact, companyAddress = values['companyName'], values['companyContact'], values['companyAddress']
        companyEmail, companyRegistrationNumber = values['companyEmail'], values['companyRegistrationNumber']
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        try:
            if UserAccount.getUserAccount(accountId) is None:
                return self._reject('Account not found.', {'accountId': ['Account not found.']}, 'not_found')
            if self.getCompanyProfile(accountId) is not None:
                return self._reject('This account already has a company profile.')
            if self._registration_exists(companyRegistrationNumber):
                message = 'The business registration number is already registered.'
                return self._reject(message, {'companyRegistrationNumber': [message]})
            self.account_id = accountId
            self.company_name, self.company_contact = companyName, companyContact
            self.company_address, self.company_email = companyAddress, companyEmail
            self.company_registration_number = companyRegistrationNumber
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return self._reject('A company profile with this account or registration number already exists.')
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @classmethod
    def getCompanyProfile(cls, accountId: str) -> 'CompanyProfile | None':
        return db.session.get(cls, accountId)

    def updateCompanyProfile(self, accountId: str, companyName: str, companyContact: str,
                             companyAddress: str, companyEmail: str,
                             companyRegistrationNumber: str) -> bool:
        values, errors = validate_company_fields(companyName, companyContact, companyAddress, companyEmail, companyRegistrationNumber)
        if errors:
            return self._reject('Please correct the errors below.', errors)
        companyName, companyContact, companyAddress = values['companyName'], values['companyContact'], values['companyAddress']
        companyEmail, companyRegistrationNumber = values['companyEmail'], values['companyRegistrationNumber']
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        try:
            profile = self.getCompanyProfile(accountId)
            if profile is None:
                return self._reject('Company profile not found.', reason='not_found')
            if self._registration_exists(companyRegistrationNumber, accountId):
                message = 'The business registration number is already registered.'
                return self._reject(message, {'companyRegistrationNumber': [message]})
            profile.company_name, profile.company_contact = companyName, companyContact
            profile.company_address, profile.company_email = companyAddress, companyEmail
            profile.company_registration_number = companyRegistrationNumber
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return self._reject('The business registration number is already registered.')
        except SQLAlchemyError:
            db.session.rollback()
            raise

    def deleteCompanyProfile(self, accountId: str) -> bool:
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        try:
            profile = self.getCompanyProfile(accountId)
            if profile is None:
                return self._reject('Company profile not found.', reason='not_found')
            db.session.delete(profile)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return self._reject('This company profile is still in use.')
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @classmethod
    def searchCompanyProfile(cls, accountId: str, keyword: str) -> list[str]:
        keyword = search_text(keyword)
        profile = cls.getCompanyProfile(accountId)
        if profile is None:
            return []
        fields = [('Company name', profile.company_name), ('Contact number', profile.company_contact),
                  ('Address', profile.company_address), ('Email', profile.company_email),
                  ('Business registration number', profile.company_registration_number)]
        return [f'{label}: {value}' for label, value in fields if keyword.casefold() in value.casefold()]
