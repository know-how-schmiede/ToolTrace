from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Tool, ToolCategory
from app.processing.pipeline import ToolProcessingPipeline

from .forms import ToolForm, UploadImageForm
from .services import ToolService, UploadService

bp = Blueprint("tools", __name__, url_prefix="/tools", template_folder="templates")


@bp.before_app_request
def seed_default_categories_once():
    if not getattr(seed_default_categories_once, "_done", False):
        ToolService().ensure_default_categories()
        seed_default_categories_once._done = True


def populate_categories(form: ToolForm) -> None:
    categories = ToolCategory.query.order_by(ToolCategory.name.asc()).all()
    form.category_id.choices = [(0, "Keine Kategorie")] + [(category.id, category.name) for category in categories]


@bp.get("/")
@login_required
def index():
    query = Tool.query.filter_by(user_id=current_user.id)
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    if q:
        query = query.filter(Tool.name.ilike(f"%{q}%"))
    if status:
        query = query.filter_by(status=status)
    tools = query.order_by(Tool.updated_at.desc()).all()
    return render_template("tools/index.html", tools=tools, q=q, status=status)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    form = ToolForm()
    populate_categories(form)
    if form.validate_on_submit():
        category_id = form.category_id.data or None
        tool = ToolService().create_tool(
            current_user.id,
            {
                "name": form.name.data,
                "category_id": category_id,
                "purpose": form.purpose.data,
                "manufacturer": form.manufacturer.data or None,
                "model": form.model.data or None,
                "inventory_number": form.inventory_number.data or None,
                "storage_location": form.storage_location.data or None,
                "description": form.description.data or None,
            },
        )
        if form.image.data:
            try:
                image = UploadService().save_source_image(tool=tool, upload=form.image.data)
                ToolProcessingPipeline().enqueue_placeholder(tool=tool, source_image=image, user_id=current_user.id)
            except ValueError as exc:
                db.session.rollback()
                flash(f"Werkzeug wurde angelegt, aber das Bild wurde nicht gespeichert: {exc}", "warning")
                return redirect(url_for("tools.detail", tool_id=tool.id))
            flash("Werkzeug wurde angelegt und das Bild wurde hochgeladen.", "success")
            return redirect(url_for("tools.detail", tool_id=tool.id))
        flash("Werkzeug wurde angelegt.", "success")
        return redirect(url_for("tools.detail", tool_id=tool.id))
    return render_template("tools/new.html", form=form)


@bp.route("/<int:tool_id>", methods=["GET", "POST"])
@login_required
def detail(tool_id: int):
    tool = ToolService().user_tool_or_404(current_user.id, tool_id)
    upload_form = UploadImageForm()
    if upload_form.validate_on_submit():
        try:
            image = UploadService().save_source_image(tool=tool, upload=upload_form.image.data)
            ToolProcessingPipeline().enqueue_placeholder(tool=tool, source_image=image, user_id=current_user.id)
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "danger")
        else:
            flash("Bild wurde hochgeladen. Die Verarbeitung ist als Platzhalterauftrag angelegt.", "success")
            return redirect(url_for("tools.detail", tool_id=tool.id))
    return render_template("tools/detail.html", tool=tool, upload_form=upload_form)
