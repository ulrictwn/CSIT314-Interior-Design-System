from sqlalchemy.exc import IntegrityError
from infrastructure.database import db
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

    def _reject(self, message, field_errors=None, reason='invalid_data'):
        self.error_message, self.field_errors, self.error_reason = message, field_errors or {}, reason
        return False

    @classmethod
    def categoryExists(cls, categoryName: str) -> bool:
        return db.session.scalar(db.select(cls.category_id).where(
            db.func.lower(cls.category_name) == categoryName.lower()).limit(1)) is not None

    def createCategory(self, categoryName: str, description: str) -> bool:
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        if self.categoryExists(categoryName):
            return self._reject('The category name already exists.', {'categoryName':['Choose a unique category name.']})
        try:
            self.category_name, self.description = categoryName, description
            db.session.add(self)
            db.session.flush()
            ActivityEvent.record('category_created', self.category_id)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return self._reject('The category name already exists.', {'categoryName':['Choose a unique category name.']})

    @classmethod
    def getCategory(cls, categoryId: int) -> 'Category | None':
        return db.session.get(cls, categoryId)

    def updateCategory(self, categoryId: int, categoryName: str, description: str) -> bool:
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        category = self.getCategory(categoryId)
        if category is None:
            return self._reject('Category not found.', reason='not_found')
        duplicate = db.session.scalar(db.select(Category.category_id).where(
            db.func.lower(Category.category_name) == categoryName.lower(), Category.category_id != categoryId).limit(1))
        if duplicate is not None:
            return self._reject('The category name already exists.', {'categoryName':['Choose a unique category name.']})
        try:
            category.category_name, category.description = categoryName, description
            ActivityEvent.record('category_updated', categoryId)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return self._reject('The category name already exists.', {'categoryName':['Choose a unique category name.']})

    def deleteCategory(self, categoryId: int) -> bool:
        self.error_message, self.field_errors, self.error_reason = None, {}, None
        category = self.getCategory(categoryId)
        if category is None:
            return self._reject('Category not found.', reason='not_found')
        if category.project_count:
            return self._reject('This category is used by projects. Assign them another category before deleting it.')
        try:
            db.session.delete(category)
            ActivityEvent.record('category_deleted', categoryId)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return self._reject('This category is still used by projects.')

    @classmethod
    def searchCategories(cls, keyword: str) -> list['Category']:
        return db.session.scalars(db.select(cls).where(db.or_(
            cls.category_name.icontains(keyword, autoescape=True),
            cls.description.icontains(keyword, autoescape=True),
            (db.literal('CAT') + db.cast(cls.category_id, db.String)).icontains(keyword, autoescape=True)))
            .order_by(cls.category_name, cls.category_id)).all()

    @property
    def project_count(self):
        from entity.projects.interior_design_project import InteriorDesignProject
        return db.session.scalar(db.select(db.func.count()).select_from(InteriorDesignProject)
            .where(InteriorDesignProject.category_id == self.category_id))

    def as_dict(self):
        return dict(categoryId=self.category_id, categoryName=self.category_name,
                    description=self.description, projectCount=self.project_count)
