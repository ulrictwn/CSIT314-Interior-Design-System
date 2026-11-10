# infrastructure/validation.py: shared pure value checks.
from infrastructure.validation import validate_category_fields, positive_integer, search_text, required_text
# infrastructure/errors.py: saved-data and validation errors.
from infrastructure.errors import DomainError
from sqlalchemy.exc import IntegrityError
# infrastructure/database.py: the shared SQLAlchemy database connection.
from infrastructure.database import db
# entity/reports/activity_event.py: dated activity records used by reports.
from entity.reports.activity_event import ActivityEvent


class Category(db.Model):
    __tablename__ = 'category'

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    __table_args__ = (
        db.Index('uq_category_name_lower', db.func.lower(category_name), unique=True),
        {'sqlite_autoincrement': True},
    )

    @classmethod
    def categoryExists(cls, categoryName: str) -> bool:
        """Check whether the category name is already stored, ignoring case."""
        categoryName = required_text(categoryName, 'Category name', 100)
        return db.session.scalar(db.select(cls.category_id).where(
            db.func.lower(cls.category_name) == categoryName.lower()).limit(1)) is not None

    def createCategory(self, categoryName: str, description: str) -> bool:
        """Check category data and duplicates, then save the new category."""
        values, errors = validate_category_fields(categoryName, description)
        if errors:
            self.error_message = 'Please correct the errors below.'
            self.field_errors = errors
            self.error_reason = 'invalid_data'
            return False
        categoryName, description = values['categoryName'], values['description']
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        if self.categoryExists(categoryName):
            self.error_message = 'The category name already exists.'
            self.field_errors = {'categoryName':['Choose a unique category name.']}
            self.error_reason = 'invalid_data'
            return False
        try:
            self.category_name, self.description = categoryName, description
            db.session.add(self)
            db.session.flush()
            ActivityEvent.record('category_created', self.category_id)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            self.error_message = 'The category name already exists.'
            self.field_errors = {'categoryName':['Choose a unique category name.']}
            self.error_reason = 'invalid_data'
            return False

    @classmethod
    def getCategory(cls, categoryId: int) -> 'Category | None':
        """Retrieve the saved category using its database ID."""
        categoryId = positive_integer(categoryId, 'Category ID')
        return db.session.get(cls, categoryId)

    def updateCategory(self, categoryId: int, categoryName: str, description: str) -> bool:
        """Check saved data and duplicate names, then update the category."""
        try:
            categoryId = positive_integer(categoryId, 'Category ID')
        except DomainError as error:
            self.error_message = str(error)
            self.field_errors = {'categoryId': [str(error)]}
            self.error_reason = 'invalid_data'
            return False
        values, errors = validate_category_fields(categoryName, description)
        if errors:
            self.error_message = 'Please correct the errors below.'
            self.field_errors = errors
            self.error_reason = 'invalid_data'
            return False
        categoryName, description = values['categoryName'], values['description']
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        category = self.getCategory(categoryId)
        if category is None:
            self.error_message = 'Category not found.'
            self.field_errors = {}
            self.error_reason = 'not_found'
            return False
        duplicate = db.session.scalar(db.select(Category.category_id).where(
            db.func.lower(Category.category_name) == categoryName.lower(), Category.category_id != categoryId).limit(1))
        if duplicate is not None:
            self.error_message = 'The category name already exists.'
            self.field_errors = {'categoryName':['Choose a unique category name.']}
            self.error_reason = 'invalid_data'
            return False
        try:
            category.category_name, category.description = categoryName, description
            ActivityEvent.record('category_updated', categoryId)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            self.error_message = 'The category name already exists.'
            self.field_errors = {'categoryName':['Choose a unique category name.']}
            self.error_reason = 'invalid_data'
            return False

    def deleteCategory(self, categoryId: int) -> bool:
        """Delete the category only when no projects reference it."""
        try:
            categoryId = positive_integer(categoryId, 'Category ID')
        except DomainError as error:
            self.error_message = str(error)
            self.field_errors = {'categoryId': [str(error)]}
            self.error_reason = 'invalid_data'
            return False
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        category = self.getCategory(categoryId)
        if category is None:
            self.error_message = 'Category not found.'
            self.field_errors = {}
            self.error_reason = 'not_found'
            return False
        if category.project_count:
            self.error_message = 'This category is used by projects. Assign them another category before deleting it.'
            self.field_errors = {}
            self.error_reason = 'invalid_data'
            return False
        try:
            db.session.delete(category)
            ActivityEvent.record('category_deleted', categoryId)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            self.error_message = 'This category is still used by projects.'
            self.field_errors = {}
            self.error_reason = 'invalid_data'
            return False

    @classmethod
    def searchCategories(cls, keyword: str) -> list['Category']:
        """Find categories matching the keyword, or list all for blank text."""
        keyword = search_text(keyword)
        return db.session.scalars(db.select(cls).where(db.or_(
            cls.category_name.icontains(keyword, autoescape=True),
            cls.description.icontains(keyword, autoescape=True),
            (db.literal('CAT') + db.cast(cls.category_id, db.String)).icontains(keyword, autoescape=True)))
            .order_by(cls.category_name, cls.category_id)).all()

    @property
    def project_count(self):
        """Count the projects that currently reference this category."""
        # entity/projects/interior_design_project.py: saved project data.
        from entity.projects.interior_design_project import InteriorDesignProject
        return db.session.scalar(db.select(db.func.count()).select_from(InteriorDesignProject)
            .where(InteriorDesignProject.category_id == self.category_id))

    def as_dict(self):
        """Return category details and project count for page or JSON display."""
        return dict(categoryId=self.category_id, categoryName=self.category_name,
                    description=self.description, projectCount=self.project_count)
