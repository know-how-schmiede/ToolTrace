"""background presets for light tables

Revision ID: 20260705_0001
Revises: 20260704_0001
Create Date: 2026-07-05
"""
from alembic import op
import sqlalchemy as sa

revision = "20260705_0001"
down_revision = "20260704_0001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("background_presets_json", sa.JSON()))
    op.add_column("source_images", sa.Column("background_key", sa.String(length=80)))
    op.add_column("source_images", sa.Column("background_name", sa.String(length=120)))
    op.add_column("source_images", sa.Column("background_width_mm", sa.Float()))
    op.add_column("source_images", sa.Column("background_height_mm", sa.Float()))


def downgrade():
    op.drop_column("source_images", "background_height_mm")
    op.drop_column("source_images", "background_width_mm")
    op.drop_column("source_images", "background_name")
    op.drop_column("source_images", "background_key")
    op.drop_column("users", "background_presets_json")
