from datetime import date, datetime
import string

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, HiddenField, BooleanField
from wtforms.fields.html5 import DateField, DateTimeField
from wtforms.validators import InputRequired, Length, Email, URL, ValidationError

from app.form_validators import SafeCharacters
from app.models import UrlModel


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[Length(max=30, message='Name cannot be longer than 30 characters!')])
    email = StringField(
        'Email address (required)',
        validators=[InputRequired('Provide email address!'), Email(message='Provide a valid email address!')]
    )
    subject = StringField('Subject (required)', validators=[InputRequired()])
    message = TextAreaField(
        'Message (required)',
        validators=[InputRequired('Provide a message!'),
                    Length(max=200, message='Message cannot be longer than 200 characters!')]
    )
    submit = SubmitField('Send')


class ReportURLForm(FlaskForm):
    REASONS = (
        ('Scamming', 'Scamming'),
        ('Inappropriate content', 'Inappropriate content'),
        ('Spam', 'Spam')
    )
    email = StringField(
        'Email address (required)',
        validators=[InputRequired('Provide email address!'), Email(message='Provide a valid email address!')]
    )
    short = StringField('Short URL (required)', validators=[InputRequired('Provide a short URL!')])
    reason = SelectField('Reason (required)', choices=REASONS, validators=[InputRequired()])
    description = TextAreaField(
        'Description (optional)',
        validators=[Length(max=200, message='Description cannot be longer than 200 characters!')]
    )
    submit = SubmitField('Send')

    def validate_short(self, short):
        short_only_chars = short.data.split('/')[-1]
        url = UrlModel.objects(short=short_only_chars).first()
        if not url:
            raise ValidationError('There is no URL as the given one in the database!')


class UrlFormMixin:
    long = StringField('Original URL', validators=[InputRequired('Provide URL!'), URL(message='URL not correct!')])
    short = StringField(
        'Short URL',
        validators=[InputRequired('Provide short URL!'),
                    Length(min=1, max=7, message='Short URL must be between 1 and 7 characters!'),
                    SafeCharacters(chars=set(string.punctuation), message='Short URL cannot have special characters!')])
    valid_til = DateTimeField('Valid Til', format='%Y-%m-%d %H:%M', validators=[InputRequired('Provide expiration date!')])
    submit = SubmitField('Update')

    def validate_valid_til(self, valid_til):
        if valid_til.data and valid_til.data < datetime.utcnow():
            raise ValidationError('You cannot pick a past date!')


class CreateUrlForm(FlaskForm, UrlFormMixin):
    short = StringField(
        'Short URL',
        validators=[Length(max=7, message='Short URL must be between 1 and 7 characters!'),
                    SafeCharacters(chars=set(string.punctuation), message='Short URL cannot have special characters!')])
    valid_til = DateTimeField('Valid Til', format='%Y-%m-%d %H:%M')
    submit = SubmitField('Shorten URL!')

    def validate_short(self, short):
        url_by_short = UrlModel.objects(short=short.data.lower()).first()
        if url_by_short:
            raise ValidationError('Short URL already exists in database!')


class UpdateUrlForm(FlaskForm, UrlFormMixin):
    url_id = HiddenField()
    submit = SubmitField('Update')

    def validate(self):
        if not super().validate():
            return False
        url = UrlModel.objects(id=self.url_id.data).first()
        urls_by_short = UrlModel.objects(short=self.short.data.lower())
        if len(urls_by_short) > 0 and not self.short.data.lower() == url.short:
            self.short.errors.append('Short URL already exists in database!')
            return False
        return True




