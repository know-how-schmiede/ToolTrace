from __future__ import annotations

import uuid
from io import BytesIO
from pathlib import Path
import shutil

from flask import current_app
from PIL import Image, ImageOps, UnidentifiedImageError
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import AuditLog, SourceImage, Tool, ToolCategory


DEFAULT_CATEGORIES = [
    "Zange",
    "Hammer",
    "Schraubenschluessel",
    "Schraubendreher",
    "Saege",
    "Messwerkzeug",
    "Elektrowerkzeug",
    "Sonstiges",
]


class ToolService:
    def ensure_default_categories(self) -> None:
        for name in DEFAULT_CATEGORIES:
            exists = ToolCategory.query.filter_by(name=name, is_global=True).first()
            if not exists:
                db.session.add(ToolCategory(name=name, is_global=True))
        db.session.commit()

    def create_tool(self, user_id: int, data: dict) -> Tool:
        tool = Tool(user_id=user_id, status="draft", **data)
        db.session.add(tool)
        db.session.flush()
        StorageService().ensure_tool_directories(user_id, tool.id)
        db.session.add(AuditLog(user_id=user_id, action="tool_created", entity_type="tool", entity_id=tool.id))
        db.session.commit()
        return tool

    def user_tool_or_404(self, user_id: int, tool_id: int) -> Tool:
        return Tool.query.filter_by(id=tool_id, user_id=user_id).first_or_404()

    def delete_tool(self, tool: Tool) -> None:
        user_id = tool.user_id
        tool_id = tool.id
        storage_service = StorageService()
        tool_root = storage_service.tool_root(user_id, tool_id)
        db.session.add(AuditLog(user_id=user_id, action="tool_deleted", entity_type="tool", entity_id=tool_id))
        db.session.delete(tool)
        db.session.commit()
        storage_service.delete_tool_directory(tool_root)


class StorageService:
    subfolders = ("source", "processed", "masks", "previews", "contours", "exports")

    def tool_root(self, user_id: int, tool_id: int) -> Path:
        return Path(current_app.config["STORAGE_PATH"]) / "users" / str(user_id) / "tools" / str(tool_id)

    def ensure_tool_directories(self, user_id: int, tool_id: int) -> Path:
        root = self.tool_root(user_id, tool_id)
        for folder in self.subfolders:
            (root / folder).mkdir(parents=True, exist_ok=True)
        return root

    def relative_to_storage(self, path: Path) -> str:
        return path.relative_to(Path(current_app.config["STORAGE_PATH"])).as_posix()

    def delete_tool_directory(self, tool_root: Path) -> None:
        storage_root = Path(current_app.config["STORAGE_PATH"]).resolve()
        resolved_tool_root = tool_root.resolve()
        if storage_root == resolved_tool_root or storage_root not in resolved_tool_root.parents:
            raise ValueError("Refusing to delete outside storage path.")
        if resolved_tool_root.exists():
            shutil.rmtree(resolved_tool_root)


class UploadService:
    mime_by_format = {"JPEG": "image/jpeg", "PNG": "image/png"}
    extension_by_format = {"JPEG": ".jpg", "PNG": ".png"}

    def save_source_image(self, *, tool: Tool, upload: FileStorage) -> SourceImage:
        original_name = secure_filename(upload.filename or "upload")
        raw = upload.read()
        if not raw:
            raise ValueError("Die Datei ist leer.")

        try:
            image = Image.open(BytesIO(raw))
            image_format = (image.format or "").upper()
            image.verify()
            image = Image.open(BytesIO(raw))
            image = ImageOps.exif_transpose(image)
        except UnidentifiedImageError as exc:
            raise ValueError("Die Datei ist kein gueltiges Bild.") from exc

        if image_format not in self.extension_by_format:
            raise ValueError("Nur JPEG- und PNG-Dateien sind erlaubt.")

        width, height = image.size

        root = StorageService().ensure_tool_directories(tool.user_id, tool.id)
        stored_name = f"{uuid.uuid4().hex}{self.extension_by_format[image_format]}"
        output_path = root / "source" / stored_name
        image.save(output_path)

        source_image = SourceImage(
            tool_id=tool.id,
            original_filename=original_name,
            stored_filename=stored_name,
            original_path=StorageService().relative_to_storage(output_path),
            mime_type=self.mime_by_format[image_format],
            file_size=len(raw),
            width_px=width,
            height_px=height,
            orientation="landscape" if width >= height else "portrait",
        )
        db.session.add(source_image)
        db.session.add(AuditLog(user_id=tool.user_id, action="image_uploaded", entity_type="tool", entity_id=tool.id))
        db.session.commit()
        return source_image


def image_resolution_warning(source_image: SourceImage) -> str | None:
    min_width = current_app.config["MIN_IMAGE_WIDTH"]
    min_height = current_app.config["MIN_IMAGE_HEIGHT"]
    if source_image.width_px >= min_width and source_image.height_px >= min_height:
        return None
    return (
        "Das Bild wurde gespeichert, ist aber kleiner als die empfohlene Mindestaufloesung "
        f"von {min_width} x {min_height} px."
    )
