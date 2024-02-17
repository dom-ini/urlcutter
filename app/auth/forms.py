from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Length, Email, EqualTo, ValidationError
from app.form_validators import SafeCharacters
from app.models import UserModel


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired('Provide username!')])
    password = PasswordField('Password', validators=[InputRequired('Provide password!')])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign in')


class SignUpForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[InputRequired('Provide username!'), SafeCharacters(field_name='Username'),
                    Length(min=5, max=25, message='Username must be between 5 and 25 characters!')]
    )
    email = StringField(
        'Email address',
        validators=[InputRequired('Provide email address!'), Email(message='Provide a valid email address!')]
    )
    password1 = PasswordField(
        'Password',
        validators=[InputRequired('Provide password!'),
                    Length(min=8, max=16, message='Password must be between 8 and 16 characters!')]
    )
    password2 = PasswordField(
        'Confirm password',
        validators=[InputRequired('Confirm password!'), EqualTo('password1', message='Passwords must match!')]
    )
    recaptcha = RecaptchaField()
    submit = SubmitField('Sign up')

    def validate_username(self, username):
        user = UserModel.objects(username=username.data.lower()).first()
        if user:
            raise ValidationError('Username already taken!')

    def validate_email(self, email):
        user = UserModel.objects(email=email.data.lower()).first()
        if user:
            raise ValidationError('Email address already exists!')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(
        'Email address',
        validators=[InputRequired('Provide email address!'), Email(message='Provide a valid email address!')]
    )
    submit = SubmitField('Reset password')


class ResetPasswordForm(FlaskForm):
    password1 = PasswordField(
        'Password',
        validators=[InputRequired('Provide password!'),
                    Length(min=8, max=16, message='Password must be between 8 and 16 characters!')]
    )
    password2 = PasswordField(
        'Confirm password',
        validators=[InputRequired('Confirm password!'), EqualTo('password1', message='Passwords must match!')]
    )
    submit = SubmitField('Set password')


class DeleteAccountForm(FlaskForm):
    email = StringField('Email address', validators=[InputRequired('Provide email address!')])
    password = PasswordField('Password', validators=[InputRequired('Provide password!')])
    submit = SubmitField('Delete my account')


class ChangeEmailRequestForm(FlaskForm):
    email = StringField(
        'New email address',
        validators=[InputRequired('Provide email address!'), Email(message='Provide a valid email address!')]
    )
    password = PasswordField('Password', validators=[InputRequired('Provide password!')])
    submit = SubmitField('Change email address')

    def validate_email(self, email):
        user = UserModel.objects(email=email.data.lower()).first()
        if user:
            raise ValidationError('Email address already exists!')
