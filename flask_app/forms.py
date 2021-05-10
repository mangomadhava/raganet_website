from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, SelectField
from wtforms.validators import (
    InputRequired,
    DataRequired,
    NumberRange,
    Length,
    Email,
    EqualTo,
    ValidationError,
)
import string

from .models import User

class AudioForm(FlaskForm):
    audio = FileField(validators=[FileRequired()])
    actual = StringField(
        "Correct Raga", validators=[Length(min=0, max=100)]
    )
    submit = SubmitField("Predict")

class MoreInfoForm(FlaskForm):
    go = SubmitField("Go")
    choose_raga = SelectField("Learn more", choices=[('https://www.ragasurabhi.com/carnatic-music/raga/raga--abheri.html', 'AbhEri'),
            ( 'https://www.ragasurabhi.com/carnatic-music/raga/raga--suddha-dhanyasi.html', 'shuddhadhanyAsi')])


class VerifyResultForm(FlaskForm):
    submit = SubmitField("Submit")
    result = SelectField("How did the model do?", choices=[('Correct', 'Correct'), ('Incorrect', 'Incorrect')])

class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min = 8)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user is not None:
            raise ValidationError("Username is taken")

    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user is not None:
            raise ValidationError("Email is taken")

    def validate_password(self, password):
        upper = any(l.isupper() for l in password.data)
        sp_chr = any(l in string.punctuation for l in password.data)
        if (not upper) or (not sp_chr):
            raise ValidationError("Password must have one uppercase and one special character")



class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")


class UpdateUsernameForm(FlaskForm):
    username = StringField(
        "New Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    submit = SubmitField("Update Username")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.objects(username=username.data).first()
            if user is not None:
                raise ValidationError("That username is already taken")
