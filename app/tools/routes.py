from __future__ import annotations

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required
from pathlib import Path
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Contour, ProcessedImage, ProcessingJob, SourceImage, Tool, ToolCategory
from app.processing.contour_extraction import ContourExtractionService
from app.processing.pipeline import ToolProcessingPipeline

from .backgrounds import background_choices_for_user, selected_background_for_user
from .forms import ToolForm, UploadImageForm
from .services import StorageService, ToolService, UploadService, image_resolution_warning

bp = Blueprint("tools", __name__, url_prefix="/tools", template_folder="templates")


@bp.before_app_request
def seed_default_categories_once():
    if not getattr(seed_default_categories_once, "_done", False):
        ToolService().ensure_default_categories()
        seed_default_categories_once._done = True


def populate_categories(form: ToolForm) -> None:
    categories = ToolCategory.query.order_by(ToolCategory.name.asc()).all()
    form.category_id.choices = [(0, "Keine Kategorie")] + [(category.id, category.name) for category in categories]


def populate_backgrounds(form: ToolForm | UploadImageForm) -> None:
    form.background_key.choices = background_choices_for_user(current_user)


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
    manual_preview_by_tool_id = {}
    if tools:
        tool_ids = [tool.id for tool in tools]
        manual_previews = (
            ProcessedImage.query.join(ProcessedImage.processing_job)
            .filter(
                ProcessedImage.image_type == "manual_aligned_contour_preview",
                ProcessedImage.processing_job.has(ProcessingJob.tool_id.in_(tool_ids)),
            )
            .order_by(ProcessedImage.created_at.desc())
            .all()
        )
        for preview in manual_previews:
            tool_id = preview.processing_job.tool_id
            if tool_id not in manual_preview_by_tool_id:
                manual_preview_by_tool_id[tool_id] = preview
    return render_template(
        "tools/index.html",
        tools=tools,
        q=q,
        status=status,
        manual_preview_by_tool_id=manual_preview_by_tool_id,
    )


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    form = ToolForm()
    populate_categories(form)
    populate_backgrounds(form)
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
            background = selected_background_for_user(current_user, form.background_key.data)
            image = UploadService().save_source_image(tool=tool, upload=upload, background=background)
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
    populate_backgrounds(upload_form)
    if upload_form.validate_on_submit():
        try:
            background = selected_background_for_user(current_user, upload_form.background_key.data)
            image = UploadService().save_source_image(tool=tool, upload=upload_form.image.data, background=background)
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
    perspective_previews = (
        ProcessedImage.query.join(ProcessedImage.processing_job)
        .filter(
            ProcessedImage.image_type == "perspective_corrected",
            ProcessedImage.processing_job.has(tool_id=tool.id),
        )
        .order_by(ProcessedImage.created_at.desc())
        .all()
    )
    mask_previews = (
        ProcessedImage.query.join(ProcessedImage.processing_job)
        .filter(ProcessedImage.image_type == "cleaned_mask", ProcessedImage.processing_job.has(tool_id=tool.id))
        .order_by(ProcessedImage.created_at.desc())
        .all()
    )
    contour_previews = (
        ProcessedImage.query.join(ProcessedImage.processing_job)
        .filter(ProcessedImage.image_type == "contour_overlay", ProcessedImage.processing_job.has(tool_id=tool.id))
        .order_by(ProcessedImage.created_at.desc())
        .all()
    )
    aligned_contour_previews = (
        ProcessedImage.query.join(ProcessedImage.processing_job)
        .filter(
            ProcessedImage.image_type == "aligned_contour_preview",
            ProcessedImage.processing_job.has(tool_id=tool.id),
        )
        .order_by(ProcessedImage.created_at.desc())
        .all()
    )
    active_contour = Contour.query.filter_by(tool_id=tool.id, is_active=True).order_by(Contour.created_at.desc()).first()
    return render_template(
        "tools/detail.html",
        tool=tool,
        upload_form=upload_form,
        page_previews=page_previews,
        perspective_previews=perspective_previews,
        mask_previews=mask_previews,
        contour_previews=contour_previews,
        aligned_contour_previews=aligned_contour_previews,
        active_contour=active_contour,
    )


@bp.post("/<int:tool_id>/contours/<int:contour_id>/manual-align")
@login_required
def manual_align_contour(tool_id: int, contour_id: int):
    tool = ToolService().user_tool_or_404(current_user.id, tool_id)
    contour = Contour.query.filter_by(id=contour_id, tool_id=tool.id, is_active=True).first_or_404()
    try:
        edge_start = (float(request.form.get("edge_start_x_mm", "")), float(request.form.get("edge_start_y_mm", "")))
        edge_end = (float(request.form.get("edge_end_x_mm", "")), float(request.form.get("edge_end_y_mm", "")))
        grid_size_raw = (request.form.get("grid_size_mm") or "").strip().replace(",", ".")
        grid_size_mm = float(grid_size_raw) if grid_size_raw else None
        if grid_size_mm is not None and grid_size_mm <= 0:
            raise ValueError("grid_size_invalid")
        geometry_data = ContourExtractionService().manual_align_geometry(
            contour.geometry_data or {},
            edge_start=edge_start,
            edge_end=edge_end,
            grid_size_mm=grid_size_mm,
        )
    except (TypeError, ValueError):
        flash("Bitte waehlen Sie zwei unterschiedliche Punkte auf einer Kante und ein gueltiges Rastermass.", "danger")
        return redirect(url_for("tools.detail", tool_id=tool.id))

    bounding_box = geometry_data["bounding_box_mm"]
    Contour.query.filter_by(tool_id=tool.id, is_active=True).update({"is_active": False})
    manual_contour = Contour(
        tool_id=tool.id,
        processing_job_id=contour.processing_job_id,
        parent_contour_id=contour.id,
        version=contour.version + 1,
        contour_type="manual_aligned",
        geometry_data=geometry_data,
        width_mm=bounding_box["width"],
        height_mm=bounding_box["height"],
        area_mm2=contour.area_mm2,
        perimeter_mm=contour.perimeter_mm,
        rotation_deg=geometry_data["alignment"]["rotation_deg"],
        is_active=True,
    )
    db.session.add(manual_contour)
    db.session.flush()

    storage_root = Path(current_app.config["STORAGE_PATH"]).resolve()
    preview_path = (
        StorageService().tool_root(tool.user_id, tool.id)
        / "contours"
        / f"manual_aligned_contour_{manual_contour.id}.png"
    )
    preview_width, preview_height = ContourExtractionService().write_geometry_preview(
        geometry_data,
        preview_path,
    )
    db.session.add(
        ProcessedImage(
            processing_job_id=contour.processing_job_id,
            image_type="manual_aligned_contour_preview",
            file_path=preview_path.relative_to(storage_root).as_posix(),
            width_px=preview_width,
            height_px=preview_height,
        )
    )
    db.session.commit()
    flash("Kontur wurde anhand der gewaehlten Kante ausgerichtet.", "success")
    return redirect(url_for("tools.detail", tool_id=tool.id))


@bp.post("/<int:tool_id>/delete")
@login_required
def delete(tool_id: int):
    tool = ToolService().user_tool_or_404(current_user.id, tool_id)
    tool_name = tool.name
    try:
        ToolService().delete_tool(tool)
    except ValueError as exc:
        db.session.rollback()
        flash(f"Werkzeug konnte nicht geloescht werden: {exc}", "danger")
        return redirect(url_for("tools.detail", tool_id=tool_id))
    flash(f"Werkzeug \"{tool_name}\" und alle zugehoerigen Dateien wurden geloescht.", "success")
    return redirect(url_for("tools.index"))


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
