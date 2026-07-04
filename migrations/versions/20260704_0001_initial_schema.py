"""initial schema

Revision ID: 20260704_0001
Revises:
Create Date: 2026-07-04
"""
from alembic import op
import sqlalchemy as sa

revision = "20260704_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=120)),
        sa.Column("last_name", sa.String(length=120)),
        sa.Column("role", sa.String(length=40), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "tool_categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("tool_categories.id")),
        sa.Column("is_global", sa.Boolean(), nullable=False),
        sa.Column("owner_user_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_tool_categories_name", "tool_categories", ["name"])

    op.create_table(
        "tools",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("tool_categories.id")),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("purpose", sa.String(length=255), nullable=False),
        sa.Column("manufacturer", sa.String(length=180)),
        sa.Column("model", sa.String(length=180)),
        sa.Column("article_number", sa.String(length=120)),
        sa.Column("serial_number", sa.String(length=120)),
        sa.Column("inventory_number", sa.String(length=120)),
        sa.Column("description", sa.Text()),
        sa.Column("notes", sa.Text()),
        sa.Column("storage_location", sa.String(length=255)),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_tools_user_id", "tools", ["user_id"])
    op.create_index("ix_tools_status", "tools", ["status"])

    op.create_table(
        "tool_tags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.UniqueConstraint("user_id", "name", name="uq_tool_tag_user_name"),
    )
    op.create_index("ix_tool_tags_user_id", "tool_tags", ["user_id"])

    op.create_table(
        "tool_tag_assignments",
        sa.Column("tool_id", sa.Integer(), sa.ForeignKey("tools.id"), primary_key=True),
        sa.Column("tag_id", sa.Integer(), sa.ForeignKey("tool_tags.id"), primary_key=True),
    )

    op.create_table(
        "source_images",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tool_id", sa.Integer(), sa.ForeignKey("tools.id"), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_filename", sa.String(length=255), nullable=False),
        sa.Column("original_path", sa.String(length=500), nullable=False),
        sa.Column("preview_path", sa.String(length=500)),
        sa.Column("mime_type", sa.String(length=120), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("width_px", sa.Integer(), nullable=False),
        sa.Column("height_px", sa.Integer(), nullable=False),
        sa.Column("orientation", sa.String(length=40)),
        sa.Column("blur_score", sa.Float()),
        sa.Column("brightness_score", sa.Float()),
        sa.Column("contrast_score", sa.Float()),
        sa.Column("page_detection_score", sa.Float()),
        sa.Column("segmentation_score", sa.Float()),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_source_images_tool_id", "source_images", ["tool_id"])

    op.create_table(
        "processing_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tool_id", sa.Integer(), sa.ForeignKey("tools.id"), nullable=False),
        sa.Column("source_image_id", sa.Integer(), sa.ForeignKey("source_images.id")),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("current_step", sa.String(length=80), nullable=False),
        sa.Column("progress_percent", sa.Integer(), nullable=False),
        sa.Column("error_code", sa.String(length=80)),
        sa.Column("error_message", sa.Text()),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_processing_jobs_tool_id", "processing_jobs", ["tool_id"])
    op.create_index("ix_processing_jobs_user_id", "processing_jobs", ["user_id"])

    op.create_table(
        "processed_images",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("processing_job_id", sa.Integer(), sa.ForeignKey("processing_jobs.id"), nullable=False),
        sa.Column("image_type", sa.String(length=80), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("width_px", sa.Integer()),
        sa.Column("height_px", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_processed_images_processing_job_id", "processed_images", ["processing_job_id"])

    op.create_table(
        "contours",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tool_id", sa.Integer(), sa.ForeignKey("tools.id"), nullable=False),
        sa.Column("processing_job_id", sa.Integer(), sa.ForeignKey("processing_jobs.id")),
        sa.Column("parent_contour_id", sa.Integer(), sa.ForeignKey("contours.id")),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("contour_type", sa.String(length=80), nullable=False),
        sa.Column("geometry_data", sa.JSON()),
        sa.Column("geometry_format", sa.String(length=40), nullable=False),
        sa.Column("width_mm", sa.Float()),
        sa.Column("height_mm", sa.Float()),
        sa.Column("area_mm2", sa.Float()),
        sa.Column("perimeter_mm", sa.Float()),
        sa.Column("rotation_deg", sa.Float(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_contours_tool_id", "contours", ["tool_id"])

    op.create_table(
        "contour_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("contour_id", sa.Integer(), sa.ForeignKey("contours.id"), nullable=False, unique=True),
        sa.Column("threshold_method", sa.String(length=80)),
        sa.Column("threshold_value", sa.Float()),
        sa.Column("smoothing_value", sa.Float()),
        sa.Column("simplification_tolerance_mm", sa.Float()),
        sa.Column("minimum_area_mm2", sa.Float()),
        sa.Column("close_gap_size", sa.Integer()),
        sa.Column("remove_small_objects", sa.Boolean(), nullable=False),
        sa.Column("include_inner_contours", sa.Boolean(), nullable=False),
        sa.Column("offset_mm", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "layouts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tool_id", sa.Integer(), sa.ForeignKey("tools.id"), nullable=False),
        sa.Column("contour_id", sa.Integer(), sa.ForeignKey("contours.id")),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("layout_type", sa.String(length=80), nullable=False),
        sa.Column("width_mm", sa.Float()),
        sa.Column("height_mm", sa.Float()),
        sa.Column("grid_size_x", sa.Integer()),
        sa.Column("grid_size_y", sa.Integer()),
        sa.Column("grid_unit_mm", sa.Float()),
        sa.Column("margin_left_mm", sa.Float(), nullable=False),
        sa.Column("margin_right_mm", sa.Float(), nullable=False),
        sa.Column("margin_top_mm", sa.Float(), nullable=False),
        sa.Column("margin_bottom_mm", sa.Float(), nullable=False),
        sa.Column("contour_offset_x_mm", sa.Float(), nullable=False),
        sa.Column("contour_offset_y_mm", sa.Float(), nullable=False),
        sa.Column("contour_rotation_deg", sa.Float(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_layouts_tool_id", "layouts", ["tool_id"])

    op.create_table(
        "exports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tool_id", sa.Integer(), sa.ForeignKey("tools.id"), nullable=False),
        sa.Column("contour_id", sa.Integer(), sa.ForeignKey("contours.id")),
        sa.Column("layout_id", sa.Integer(), sa.ForeignKey("layouts.id")),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("export_type", sa.String(length=40), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("options_json", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_exports_tool_id", "exports", ["tool_id"])
    op.create_index("ix_exports_user_id", "exports", ["user_id"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("entity_type", sa.String(length=120)),
        sa.Column("entity_id", sa.Integer()),
        sa.Column("details_json", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])


def downgrade():
    for table in [
        "audit_logs",
        "exports",
        "layouts",
        "contour_settings",
        "contours",
        "processed_images",
        "processing_jobs",
        "source_images",
        "tool_tag_assignments",
        "tool_tags",
        "tools",
        "tool_categories",
        "users",
    ]:
        op.drop_table(table)
