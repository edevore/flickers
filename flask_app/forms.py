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
    phone = StringField("Phone", validators=[DataRequired(), Length(min=10, max=10)])
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

    def validate_phone(self, phone):
        # try:
        #     p = phonenumbers.parse(phone.data)
        #     p = "+1 " + p
        #     if not phonenumbers.is_valid_number(p):
        #         raise ValueError()
        # except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
        #     raise ValidationError('Invalid phone number')
        s = phone.data
        nums = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        for c in s:
            if c not in nums:
                raise ValidationError("Number is invalid. Used a non-numeric character.")
        
        # Make sure phone number is unique
        user = User.objects(phone=phone.data).first()
        if user is not None:
            raise ValidationError("Phone number is taken by another user") 
        

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
    token = StringField('Token (from validator app)', validators=[InputRequired(), Length(min=6, max=6)])
    submit = SubmitField("Login")

    def validate_token(self, token):
        user = User.objects(username=self.username.data).first()
        if user is not None:
            tok_verified = pyotp.TOTP(user.otp_secret).verify(token.data)
            if not tok_verified:
                raise ValidationError("Invalid Token")



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
