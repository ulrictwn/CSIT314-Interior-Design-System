from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SelectMultipleField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms.widgets import CheckboxInput, ListWidget
from infrastructure.permissions import PERMISSION_OPTIONS


class ActionForm(FlaskForm):
    submit = SubmitField('Confirm')


class CreateUserProfileForm(FlaskForm):
    profileName = StringField('Profile Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=10000)])
    status = SelectField('Status', choices=[('', 'Select status'), ('Active', 'Active'), ('Suspended', 'Suspended')], validators=[DataRequired()])
    permissions = SelectMultipleField('Permissions', choices=list(PERMISSION_OPTIONS.items()),
        widget=ListWidget(prefix_label=False), option_widget=CheckboxInput(), default=list)
    submit = SubmitField('Create')


class CreateUserAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80), Regexp(r'^[A-Za-z0-9_.-]+$')])
    full_name = StringField('Full name', validators=[DataRequired(), Length(max=120)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=254)])
    phone_number = StringField('Phone number', validators=[DataRequired(), Length(max=40)])
    profile_id = SelectField('Assigned profile', coerce=int, choices=[], validators=[DataRequired()])
    submit = SubmitField('Create')


class UpdateUserAccountForm(FlaskForm):
    full_name = StringField('Full name', validators=[DataRequired(), Length(max=120)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=254)])
    profile_id = SelectField('Assigned profile', coerce=int, choices=[], validators=[DataRequired()])
    submit = SubmitField('Update Account')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=128)])
    submit = SubmitField('Login')
