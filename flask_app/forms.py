from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
import phonenumbers
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, PasswordField, RadioField, FieldList, FormField
from wtforms.validators import (
    InputRequired,
    DataRequired,
    NumberRange,
    Length,
    Email,
    EqualTo,
    ValidationError,
    Regexp
)
import pyotp
from .models import User, Group

class SearchForm(FlaskForm):
    search_query = StringField(
        "Query", validators=[InputRequired(), Length(min=1, max=100)]
    )
    submit = SubmitField("Search")

    def validate_search_query(self, search_query):
        group = Group.objects(group_id=search_query.data).first()
        if group is None:
            raise ValidationError(f"Group with ID=\"{search_query.data}\" does not exist.")

class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    first_name = StringField(
        "First Name", validators=[InputRequired()]
    )
    last_name = StringField(
        "Last Name", validators=[InputRequired()]
    )
    email = StringField("Email", validators=[InputRequired(), Email()])
    # Regex for at least 8 letters, 1 Uppercase, 1 lowercase, 1 special, 1 number
    password = PasswordField("Password", validators=[InputRequired(), Regexp("^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$", 
        message="Password must be at least 8 characters, including 1 Uppercase letter, 1 lowercase letter, 1 number, and 1 special character [#$!@$%^&*-]")])
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user is not None:
            raise ValidationError("Username is taken by another user")

    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user is not None:
            raise ValidationError("Email is taken by another user")
        
class GroupForm(FlaskForm):
    group_id = StringField(
        "Group ID", validators=[InputRequired(), Length(min=5, max=40)]
    )
    description = TextAreaField(
        "Description", validators=[InputRequired(), Length(min=5, max=500)]
    )
    submit = SubmitField("Create Group")

    def validate_group_id(self, group_id):
        group = Group.objects(group_id=group_id.data).first()
        if group is not None:
            raise ValidationError("Group ID is taken by another group")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")

class UpdateUsernameForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    submit = SubmitField("Update Username")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.objects(username=username.data).first()
            if user is not None:
                raise ValidationError("That username is already taken")

class JoinForm(FlaskForm):
    join = SubmitField("Join")

class NextPollForm(FlaskForm):
    next = SubmitField("Advance to Next Poll")

class GoToNewPollForm(FlaskForm):
    new_poll = SubmitField("Create a New Poll")

class ChartForm(FlaskForm):
    gen_chart = SubmitField("Generate Chart")

class CreatePollForm(FlaskForm):
    question = StringField("Question", validators=[InputRequired(), Length(min=5, max=40)])
    submit = SubmitField("Create Poll")

class PollResponseForm(FlaskForm):
    choices = RadioField("Choices", choices=[("Yes", "Yes"), ("No", "No"), ("Abstain", "Abstain")])
    submit = SubmitField("Submit Response")
