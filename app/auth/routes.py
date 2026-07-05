from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.models import User
from app.tools.backgrounds import cm_to_mm, format_mm_as_cm, user_background_presets

from .forms import BackgroundSettingsForm, LoginForm, RegisterForm
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


@bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    form = BackgroundSettingsForm()
    preset_by_key = {preset.key: preset for preset in user_background_presets(current_user)}
    fields_by_key = {
        "light_table_a4": (form.a4_width_cm, form.a4_height_cm),
        "light_table_a5": (form.a5_width_cm, form.a5_height_cm),
        "light_table_a3": (form.a3_width_cm, form.a3_height_cm),
    }
    if request.method == "GET":
        for key, (width_field, height_field) in fields_by_key.items():
            preset = preset_by_key[key]
            width_field.data = format_mm_as_cm(preset.width_mm)
            height_field.data = format_mm_as_cm(preset.height_mm)

    if form.validate_on_submit():
        try:
            presets = []
            for key, (width_field, height_field) in fields_by_key.items():
                preset = preset_by_key[key]
                presets.append(
                    {
                        "key": key,
                        "name": preset.name,
                        "width_mm": cm_to_mm(width_field.data),
                        "height_mm": cm_to_mm(height_field.data),
                    }
                )
        except ValueError:
            flash("Bitte geben Sie gueltige Hintergrundgroessen in Zentimetern ein.", "danger")
        else:
            current_user.background_presets_json = presets
            db.session.commit()
            flash("Einstellungen wurden gespeichert.", "success")
            return redirect(url_for("auth.settings"))
    return render_template("auth/settings.html", form=form)


@bp.get("/forgot-password")
def forgot_password():
    return render_template("auth/forgot_password.html")
