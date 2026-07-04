from __future__ import annotations

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required
from pathlib import Path
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import ProcessedImage, SourceImage, Tool, ToolCategory
from app.processing.pipeline import ToolProcessingPipeline

from .forms import ToolForm, UploadImageForm
from .services import ToolService, UploadService, image_resolution_warning

bp = Blueprint("tools", __name__, url_prefix="/tools", template_folder="templates")


@bp.before_app_request
def seed_default_categories_once():
    if not getattr(seed_default_categories_once, "_done", False):
        ToolService().ensure_default_categories()
        seed_default_categories_once._done = True


def populate_categories(form: ToolForm) -> None:
    categories = ToolCategory.query.order_by(ToolCategory.name.asc()).all()
    form.category_id.choices = [(0, "Keine Kategorie")] + [(category.id, category.name) for category in categories]


def default_tool_name_from_upload(filename: str | None) -> str:
    safe_name = secure_filename(filename or "")
    stem = Path(safe_name).stem.strip()
    return stem[:180] or "Unbenanntes Werkzeug"


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
        upload = form.image.data
        tool_name = form.name.data.strip() if form.name.data else default_tool_name_from_upload(upload.filename)
        tool = ToolService().create_tool(
            current_user.id,
            {
                "name": tool_name,
                "category_id": category_id,
                "purpose": form.purpose.data.strip() if form.purpose.data else "",
                "manufacturer": form.manufacturer.data or None,
                "model": form.model.data or None,
                "inventory_number": form.inventory_number.data or None,
                "storage_location": form.storage_location.data or None,
                "description": form.description.data or None,
            },
        )
        try:
            image = UploadService().save_source_image(tool=tool, upload=upload)
            job = ToolProcessingPipeline().enqueue_placeholder(tool=tool, source_image=image, user_id=current_user.id)
            ToolProcessingPipeline().run(job.id)
        except ValueError as exc:
            db.session.rollback()
            db.session.delete(tool)
            db.session.commit()
            flash(f"Das Werkzeug wurde nicht gespeichert: {exc}", "danger")
            return render_template("tools/new.html", form=form)
        warning = image_resolution_warning(image)
        if warning:
            flash(warning, "warning")
        flash("Werkzeug wurde angelegt und das Bild wurde hochgeladen.", "success")
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
            job = ToolProcessingPipeline().enqueue_placeholder(tool=tool, source_image=image, user_id=current_user.id)
            ToolProcessingPipeline().run(job.id)
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "danger")
        else:
            warning = image_resolution_warning(image)
            if warning:
                flash(warning, "warning")
            flash("Bild wurde hochgeladen. Die Verarbeitung ist als Platzhalterauftrag angelegt.", "success")
            return redirect(url_for("tools.detail", tool_id=tool.id))
    page_previews = (
        ProcessedImage.query.join(ProcessedImage.processing_job)
        .filter(ProcessedImage.image_type == "page_detected", ProcessedImage.processing_job.has(tool_id=tool.id))
        .order_by(ProcessedImage.created_at.desc())
        .all()
    )
    return render_template("tools/detail.html", tool=tool, upload_form=upload_form, page_previews=page_previews)


@bp.get("/<int:tool_id>/images/<int:image_id>")
@login_required
def source_image(tool_id: int, image_id: int):
    tool = ToolService().user_tool_or_404(current_user.id, tool_id)
    image = SourceImage.query.filter_by(id=image_id, tool_id=tool.id).first_or_404()
    storage_root = Path(current_app.config["STORAGE_PATH"]).resolve()
    image_path = (storage_root / image.original_path).resolve()
    if storage_root not in image_path.parents:
        abort(404)
    if not image_path.is_file():
        abort(404)
    return send_file(image_path, mimetype=image.mime_type, max_age=3600)


@bp.get("/<int:tool_id>/processed-images/<int:processed_image_id>")
@login_required
def processed_image(tool_id: int, processed_image_id: int):
    tool = ToolService().user_tool_or_404(current_user.id, tool_id)
    image = (
        ProcessedImage.query.join(ProcessedImage.processing_job)
        .filter(ProcessedImage.id == processed_image_id, ProcessedImage.processing_job.has(tool_id=tool.id))
        .first_or_404()
    )
    storage_root = Path(current_app.config["STORAGE_PATH"]).resolve()
    image_path = (storage_root / image.file_path).resolve()
    if storage_root not in image_path.parents:
        abort(404)
    if not image_path.is_file():
        abort(404)
    return send_file(image_path, mimetype="image/png", max_age=3600)
