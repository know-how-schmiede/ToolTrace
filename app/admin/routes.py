from flask import Blueprint, abort, render_template
from flask_login import current_user, login_required

from app.models import ProcessingJob, ToolCategory, User

bp = Blueprint("admin", __name__, url_prefix="/admin", template_folder="templates")


@bp.before_request
@login_required
def require_admin():
    if not current_user.is_admin:
        abort(403)


@bp.get("/")
def index():
    return render_template(
        "admin/index.html",
        users_count=User.query.count(),
        categories_count=ToolCategory.query.count(),
        jobs_count=ProcessingJob.query.count(),
    )
