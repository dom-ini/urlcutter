from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user
from mongoengine import errors
from werkzeug.security import generate_password_hash

from app.auth import bp
from app.auth.email import (
    send_confirmation_email,
    send_email_address_change_email,
    send_email_address_change_notification_email,
    send_password_reset_email,
)
from app.auth.forms import (
    ChangeEmailRequestForm,
    DeleteAccountForm,
    LoginForm,
    ResetPasswordForm,
    ResetPasswordRequestForm,
    SignUpForm,
)
from app.models import UserModel


@bp.route("/user/<username>/change-email/<token>")
@login_required
def change_email_view(username, token):
    if not current_user.username == username:
        return redirect(url_for("main.index_view"))
    user, new_email = UserModel.verify_email_change_token(token)
    if not user:
        flash("Invalid token!")
        return redirect(url_for("main.index_view"))
    old_email = user.email
    send_email_address_change_notification_email(user, old_email)
    user.email = new_email
    try:
        user.save()
    except errors.ValidationError:
        flash("Something went wrong!", "error")
        return redirect(url_for("main.account_settings_view", username=current_user.username))
    flash("Email address on your account has been changed.", "success")
    return redirect(url_for("main.account_settings_view", username=current_user.username))


@bp.route("/user/<username>/change-email", methods=["GET", "POST"])
@login_required
def change_email_request_view(username):
    if not current_user.username == username:
        return redirect(url_for("main.index_view"))
    form = ChangeEmailRequestForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data
        user = UserModel.objects(username=current_user.username).first()
        if not user.check_password(password):
            flash("Invalid password!", "error")
            return redirect(url_for("auth.change_email_request_view", username=current_user.username))
        send_email_address_change_email(user, email)
        flash(
            "Check your new email for the confirmation link to change email address.",
            "success",
        )
        return redirect(url_for("main.account_settings_view", username=current_user.username))
    return render_template("auth/change_email_request.html", form=form)


@bp.route("/password-reset/<token>", methods=["GET", "POST"])
def reset_password_view(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.index_view"))
    user = UserModel.verify_reset_password_token(token)
    if not user:
        return redirect(url_for("main.index_view"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        password1 = form.password1.data
        user.set_password(password1)
        try:
            user.save()
        except errors.ValidationError:
            flash("Something went wrong!", "error")
            return redirect(url_for("auth.login_view"))
        flash("Password changed successfully!", "success")
        return redirect(url_for("auth.login_view"))
    return render_template("auth/reset_password.html", form=form)


@bp.route("/password-reset", methods=["GET", "POST"])
def reset_password_request_view():
    if current_user.is_authenticated:
        return redirect(url_for("main.index_view"))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        user = UserModel.objects(email=email).first()
        if user:
            send_password_reset_email(user)
            flash(
                "Check your email for the instructions to reset your password.",
                "success",
            )
            return redirect(url_for("auth.login_view"))
        flash("User with the given email address not found!", "error")
    return render_template("auth/reset_password_request.html", form=form)


@bp.route("/login", methods=["POST", "GET"])
def login_view():
    if current_user.is_authenticated:
        return redirect(url_for("main.index_view"))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.lower()
        password = form.password.data
        remember = form.remember.data
        user = UserModel.objects(username=username).first()
        if not user or not user.check_password(password) or user.disabled:
            flash("Invalid credentials!", "error")
            return redirect(url_for("auth.login_view"))
        if not user.is_activated:
            flash("The account hasn't been activated yet!", "error")
            return redirect(url_for("auth.login_view"))
        login_user(user, remember=remember)
        return redirect(url_for("main.index_view"))
    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout_view():
    logout_user()
    return redirect(url_for("main.index_view"))


@bp.route("/sign-up", methods=["POST", "GET"])
def sign_up_view():
    if current_user.is_authenticated:
        return redirect(url_for("main.index_view"))
    form = SignUpForm()
    if form.validate_on_submit():
        username = form.username.data.lower()
        email = form.email.data.lower()
        password1 = form.password1.data
        new_user = UserModel(
            username=username,
            password_hash=generate_password_hash(password1, method="sha256"),
            email=email,
        )
        try:
            new_user.save()
        except errors.ValidationError:
            flash("Please provide correct data!", "error")
            return redirect(url_for("auth.sign_up_view"))
        send_confirmation_email(new_user)
        flash("The activation link has been sent to the given email address.", "success")
        return redirect(url_for("auth.login_view"))
    return render_template("auth/sign_up.html", form=form)


@bp.route("/confirm-email/<token>")
def confirm_email_view(token):
    user = UserModel.verify_email_confirmation_token(token)
    if not user:
        flash("No user found!", "error")
        return redirect(url_for("auth.login_view"))
    user.activate()
    try:
        user.save()
    except errors.ValidationError:
        flash("There was an error during handling the request!", "error")
        return redirect(url_for("auth.login_view"))
    flash("Account activated successfully!", "success")
    return redirect(url_for("auth.login_view"))


@bp.route("/user/<username>/delete_account", methods=["GET", "POST"])
@login_required
def delete_account_view(username):
    if not current_user.username == username:
        return redirect(url_for("main.index_view"))
    form = DeleteAccountForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data
        user = UserModel.objects(username=username).first()
        if user.email != email or not user.check_password(password):
            flash("Invalid credentials!", "error")
            return redirect(url_for("auth.delete_account_view", username=current_user.username))
        user.disabled = "aaaa"
        try:
            user.save()
        except errors.ValidationError:
            flash("There was an issue when deleting account, try again.", "error")
            return redirect(url_for("auth.delete_account_view", username=current_user.username))
        flash("Account has been deleted!", "success")
        return redirect(url_for("auth.logout_view"))
    return render_template("auth/delete_account.html", form=form)
