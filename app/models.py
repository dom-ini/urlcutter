from flask_login import UserMixin
from datetime import datetime
from dateutil.relativedelta import relativedelta
from time import time
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from app import db, login_manager


class UserModel(UserMixin, db.Document):
    username = db.StringField()
    email = db.EmailField()
    password_hash = db.StringField()
    activated = db.BooleanField(default=False)
    disabled = db.BooleanField(default=False)
    joined_at = db.DateTimeField()

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': str(self.id), 'exp': time() + expires_in},
                          current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            user_id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms='HS256')['reset_password']
        except:
            return
        return UserModel.objects(id=user_id).first()

    def get_email_confirmation_token(self, expires_in=3600):
        return jwt.encode({'email_address': self.email, 'exp': time() + expires_in},
                          current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_email_confirmation_token(token):
        try:
            email = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms='HS256')['email_address']
        except:
            return
        return UserModel.objects(email=email).first()

    def get_email_change_token(self, new_email, expires_in=3600):
        return jwt.encode({'email_address': self.email, 'new_email_address': new_email, 'exp': time() + expires_in},
                          current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_email_change_token(token):
        try:
            email_old = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms='HS256')['email_address']
            email_new = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms='HS256')['new_email_address']
        except:
            return
        return UserModel.objects(email=email_old).first(), email_new

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def activate(self):
        self.activated = True

    def save(self, *args, **kwargs):
        if not self.joined_at:
            self.joined_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    @property
    def is_activated(self):
        return self.activated


class UrlModel(db.Document):
    long = db.URLField(required=True, null=False)
    short = db.StringField(required=True, null=False)
    created_at = db.DateTimeField()
    modified_at = db.DateTimeField()
    valid_til = db.DateTimeField()
    user = db.StringField(required=False)

    def __repr__(self):
        return f'<URL {self.long} > {self.short}>'

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.modified_at = datetime.utcnow()
        if not self.valid_til:
            self.valid_til = self.created_at + relativedelta(years=2)
        return super().save(*args, **kwargs)


@login_manager.user_loader
def load_user(user_id):
    return UserModel.objects.get(id=user_id)
