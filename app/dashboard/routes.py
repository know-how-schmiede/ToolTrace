from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app.models import Export, ProcessingJob, Tool

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard", template_folder="templates")


@bp.get("/")
@login_required
def index():
    tools = (
        Tool.query.filter_by(user_id=current_user.id)
        .order_by(Tool.updated_at.desc())
        .limit(6)
        .all()
    )
    total_tools = Tool.query.filter_by(user_id=current_user.id).count()
    failed_jobs = ProcessingJob.query.filter_by(user_id=current_user.id, status="failed").count()
    recent_exports = (
        Export.query.filter_by(user_id=current_user.id)
        .order_by(Export.created_at.desc())
        .limit(5)
        .all()
    )
    return render_template(
        "dashboard/index.html",
        tools=tools,
        total_tools=total_tools,
        failed_jobs=failed_jobs,
        recent_exports=recent_exports,
    )
