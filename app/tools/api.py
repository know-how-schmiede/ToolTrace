from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Tool
from app.tools.services import ToolService

bp = Blueprint("tools_api", __name__, url_prefix="/api/tools")


@bp.get("")
@login_required
def list_tools():
    tools = Tool.query.filter_by(user_id=current_user.id).order_by(Tool.updated_at.desc()).all()
    return jsonify([serialize_tool(tool) for tool in tools])


@bp.post("")
@login_required
def create_tool():
    payload = request.get_json(silent=True) or {}
    required = {"name", "purpose"}
    if not required.issubset(payload):
        return jsonify({"error": "name and purpose are required"}), 400
    tool = ToolService().create_tool(
        current_user.id,
        {
            "name": payload["name"],
            "purpose": payload["purpose"],
            "category_id": payload.get("category_id"),
        },
    )
    return jsonify(serialize_tool(tool)), 201


@bp.get("/<int:tool_id>")
@login_required
def get_tool(tool_id: int):
    tool = ToolService().user_tool_or_404(current_user.id, tool_id)
    return jsonify(serialize_tool(tool))


@bp.patch("/<int:tool_id>")
@login_required
def update_tool(tool_id: int):
    tool = ToolService().user_tool_or_404(current_user.id, tool_id)
    payload = request.get_json(silent=True) or {}
    for field in ("name", "purpose", "manufacturer", "model", "inventory_number", "storage_location", "status"):
        if field in payload:
            setattr(tool, field, payload[field])
    db.session.commit()
    return jsonify(serialize_tool(tool))


@bp.delete("/<int:tool_id>")
@login_required
def delete_tool(tool_id: int):
    tool = ToolService().user_tool_or_404(current_user.id, tool_id)
    db.session.delete(tool)
    db.session.commit()
    return "", 204


def serialize_tool(tool: Tool) -> dict:
    return {
        "id": tool.id,
        "name": tool.name,
        "purpose": tool.purpose,
        "status": tool.status,
        "category": tool.category.name if tool.category else None,
        "updated_at": tool.updated_at.isoformat() if tool.updated_at else None,
    }
