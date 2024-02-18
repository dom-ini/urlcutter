from flask import current_app, render_template

from app.email import send_email


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    subject = "[URL Cutter] Reset Your Password"
    send_email(
        subject=subject,
        recipients=[user.email],
        text_body=render_template("email/reset_password_mail.txt", user=user, token=token),
        html_body=render_template("email/reset_password_mail.html", user=user, token=token),
        sender=current_app.config["MAIL_USERNAME"],
    )


def send_confirmation_email(user):
    token = user.get_email_confirmation_token()
    subject = "[URL Cutter] Confirm Your Email Address"
    send_email(
        subject=subject,
        recipients=[user.email],
        text_body=render_template("email/confirm_mail.txt", user=user, token=token),
        html_body=render_template("email/confirm_mail.html", user=user, token=token),
        sender=current_app.config["MAIL_USERNAME"],
    )


def send_email_address_change_email(user, new_email):
    token = user.get_email_change_token(new_email)
    subject = "[URL Cutter] Confirm Email Address Change"
    send_email(
        subject=subject,
        recipients=[new_email],
        text_body=render_template("email/confirm_email_change_mail.txt", user=user, token=token),
        html_body=render_template("email/confirm_email_change_mail.html", user=user, token=token),
        sender=current_app.config["MAIL_USERNAME"],
    )


def send_email_address_change_notification_email(user, old_email):
    subject = "[URL Cutter] Email address change"
    send_email(
        subject=subject,
        recipients=[old_email],
        text_body=render_template("email/notification_email_change_mail.txt", user=user),
        html_body=render_template("email/notification_email_change_mail.html", user=user),
        sender=current_app.config["MAIL_USERNAME"],
    )
