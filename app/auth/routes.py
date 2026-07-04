from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from app.models import User

from .forms import LoginForm, RegisterForm
from .services import AuthService

bp = Blueprint("auth", __name__, url_prefix="", template_folder="templates")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = AuthService().register_user(
                email=form.email.data,
                username=form.username.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
            )
        except ValueError as exc:
            flash(str(exc), "danger")
        else:
            login_user(user)
            flash("Ihr Konto wurde erstellt.", "success")
            return redirect(url_for("dashboard.index"))
    return render_template("auth/register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.is_active and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            AuthService().record_login(user)
            next_url = request.args.get("next")
            return redirect(next_url or url_for("dashboard.index"))
        flash("Anmeldung fehlgeschlagen.", "danger")
    return render_template("auth/login.html", form=form)


@bp.post("/logout")
def logout():
    logout_user()
    flash("Sie wurden abgemeldet.", "info")
    return redirect(url_for("auth.login"))


@bp.get("/forgot-password")
def forgot_password():
    return render_template("auth/forgot_password.html")
