from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    SelectMultipleField,
    SubmitField
)
from wtforms.validators import DataRequired, Length
from wtforms.widgets import CheckboxInput, ListWidget

from control.create_user_profile_controller import (
    CreateUserProfileController
)


class CreateUserProfileForm(FlaskForm):

    profileName = StringField(
        "Profile Name",
        validators=[DataRequired(), Length(max=100)]
    )

    description = TextAreaField(
        "Description",
        validators=[DataRequired()]
    )

    status = SelectField(
        "Status",
        choices=[
            ("", "Select status"),
            ("Active", "Active"),
            ("Suspended", "Suspended")
        ],
        validators=[DataRequired()]
    )

    permissions = SelectMultipleField(
        "Permissions",
        choices=list(
            CreateUserProfileController.PERMISSION_OPTIONS.items()
        ),
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput(),
        default=list
    )

    submit = SubmitField("Create")