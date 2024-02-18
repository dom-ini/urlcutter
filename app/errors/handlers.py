from flask import render_template

from app.errors import bp


@bp.app_errorhandler(404)
def error_404_view(error):
    return render_template("errors/404.html"), 404


@bp.app_errorhandler(500)
def error_500_view(error):
    return render_template("errors/500.html"), 500
