from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from flask import abort, current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from mongoengine import errors

from app.email import send_email
from app.main import bp
from app.main.forms import ContactForm, CreateUrlForm, ReportURLForm, UpdateUrlForm
from app.main.utilities import shorten_url
from app.models import UrlModel


@bp.route("/contact", methods=["GET", "POST"])
def contact_view():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        sender_email = form.email.data
        subject = form.subject.data
        message = form.message.data
        context = {
            "name": name,
            "sender_email": sender_email,
            "subject": subject,
            "message": message,
        }
        send_email(
            subject="[CONTACT] " + subject,
            recipients=[current_app.config["MAIL_USERNAME"]],
            text_body=render_template("email/contact_mail.txt", **context),
            html_body=render_template("email/contact_mail.html", **context),
            sender="",
        )
        flash("Message has been sent!", "success")
        return redirect(url_for("main.contact_view"))
    email = current_user.email if current_user.is_authenticated else None
    return render_template("contact.html", form=form, email=email)


@bp.route("/report", methods=["GET", "POST"])
def report_url_view():
    form = ReportURLForm()
    if form.validate_on_submit():
        sender_email = form.email.data
        short = form.short.data.split("/")[-1]
        url = UrlModel.objects(short=short).first()
        long = url.long
        reason = form.reason.data
        description = form.description.data
        context = {
            "sender_email": sender_email,
            "short": short,
            "long": long,
            "reason": reason,
            "description": description,
        }
        send_email(
            subject=f"[REPORT] {reason} - {short}",
            recipients=[current_app.config["MAIL_USERNAME"]],
            text_body=render_template("email/report_mail.txt", **context),
            html_body=render_template("email/report_mail.html", **context),
            sender="",
        )
        flash("Message has been sent!", "success")
        return redirect(url_for("main.report_url_view"))
    email = current_user.email if current_user.is_authenticated else None
    return render_template("report_url.html", form=form, email=email)


@bp.route("/user/<username>")
@login_required
def user_view(username):
    if current_user.username == username:
        urls = UrlModel.objects(user=username)
        context = {"urls": urls}
        return render_template("user.html", **context)
    return redirect(url_for("main.index_view"))


@bp.route("/user/<username>/settings")
@login_required
def account_settings_view(username):
    if current_user.username == username:
        return render_template("account_settings.html")
    return redirect(url_for("main.index_view"))


@bp.route("/update/<url_id>", methods=["GET", "POST"])
@login_required
def update_url_view(url_id):
    url = UrlModel.objects(id=url_id).first_or_404()
    if url.user != current_user.username:
        return redirect(url_for("main.index_view"))
    form = UpdateUrlForm()
    if form.validate_on_submit():
        long = form.long.data
        short = form.short.data.lower()
        valid_til = form.valid_til.data
        url.long = long
        url.short = short
        url.valid_til = valid_til
        try:
            url.save()
        except errors.ValidationError:
            flash("There was an issue when trying to update URL!", "error")
            return redirect(url_for("main.update_url_view", url_id=url.id))
        flash("URL has been updated!", "success")
        return redirect(url_for("main.user_view", username=current_user.username))
    context = {"url": url, "form": form}
    return render_template("update_url.html", **context)


@bp.route("/shorten", methods=["POST"])
def shorten_url_view():
    form = CreateUrlForm()
    if form.validate_on_submit():
        long = form.long.data
        custom_short = form.short.data.lower() if request.form.get("custom_short_check") else ""
        valid_til = form.valid_til.data if request.form.get("custom_valid_til_check") else None
        user = current_user.username if current_user.is_authenticated else None
        short = shorten_url(long) if not custom_short else custom_short
        new_url = UrlModel(long=long, short=short, valid_til=valid_til)
        if user:
            new_url.user = user
        try:
            new_url.save()
        except errors.ValidationError:
            flash("Provide a valid URL!", "error")
            return redirect(url_for("main.index_view"))
        return jsonify(data={"response": short})
    return jsonify(data=form.errors)


@bp.route("/", methods=["GET", "POST"])
def index_view():
    form = CreateUrlForm()
    default_lifespan = datetime.utcnow() + relativedelta(years=current_app.config["DEFAULT_LIFESPAN_Y"])
    context = {"default_lifespan": default_lifespan, "form": form}
    return render_template("index.html", **context)


@bp.route("/<short>")
def go_to_original_view(short):
    original_url = UrlModel.objects(short=short.lower()).first_or_404()
    if original_url.valid_til.date() < date.today():
        original_url.delete()
        abort(404)
    return redirect(original_url.long)


@bp.route("/delete/<url_id>")
@login_required
def delete_url_view(url_id):
    url = UrlModel.objects(id=url_id).first_or_404()
    if url.user == current_user.username:
        url.delete()
        flash("URL has been deleted!", "success")
        return redirect(url_for("main.user_view", username=current_user.username))
    return redirect(url_for("main.index_view"))
