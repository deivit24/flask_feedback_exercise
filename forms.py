from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
# RadioField, SelectField, BooleanField, IntegerField, FloatField 
from wtforms.validators import InputRequired, Length, Email, EqualTo

# FORM CLASSES GO BELOW!

class UserForm(FlaskForm):
    first_name = StringField("First Name", validators=[InputRequired(), Length(min=1, max=30, message=" first name must be between %(min)d and %(max)d characters long")])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(min=1, max=30, message=" last name must be between %(min)d and %(max)d characters long")])
    username = StringField("Username", validators=[InputRequired(), Length(min=3, max=20, message=" username must be between %(min)d and %(max)d characters long")])
    email = StringField("Email", validators=[InputRequired(), Email(message="Must be a valid Email")])
    password = PasswordField('Password', [InputRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm  = PasswordField('Confirm Password')

class LoginForm(FlaskForm):
      username = StringField("Username", validators=[InputRequired(), Length(min=3, max=20, message=" username must be between %(min)d and %(max)d characters long")])

      password = PasswordField('Password', [InputRequired()])


class FeedbackForm(FlaskForm):
    """Add feedback form."""

    title = StringField(
        "Title",
        validators=[InputRequired(), Length(max=100, message=" Tile must be less than %(max)d characters long")],
    )
    content = StringField(
        "Content",
        validators=[InputRequired()],
    )


class DeleteForm(FlaskForm):
    """Delete form -- this form is intentionally blank."""