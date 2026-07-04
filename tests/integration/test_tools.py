from __future__ import annotations

from io import BytesIO

from PIL import Image

from app.models import ProcessingJob, SourceImage, Tool
from tests.conftest import register_and_login


def test_user_can_create_tool(client, app):
    register_and_login(client)

    response = client.post(
        "/tools/new",
        data={
            "name": "Kombizange",
            "category_id": "0",
            "purpose": "Schaumstoffeinlage",
            "manufacturer": "Knipex",
            "model": "Demo",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Kombizange" in response.get_data(as_text=True)

    with app.app_context():
        tool = Tool.query.filter_by(name="Kombizange").one()
        assert tool.status == "draft"
        assert tool.purpose == "Schaumstoffeinlage"


def test_image_upload_stores_metadata_and_placeholder_job(client, app):
    register_and_login(client)
    client.post(
        "/tools/new",
        data={"name": "Hammer", "category_id": "0", "purpose": "Shadowboard"},
        follow_redirects=True,
    )

    image_bytes = BytesIO()
    Image.new("RGB", (20, 20), "white").save(image_bytes, format="PNG")
    image_bytes.seek(0)

    response = client.post(
        "/tools/1",
        data={"image": (image_bytes, "hammer.png")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Bild wurde hochgeladen" in response.get_data(as_text=True)

    with app.app_context():
        source_image = SourceImage.query.one()
        job = ProcessingJob.query.one()
        assert source_image.original_filename == "hammer.png"
        assert source_image.width_px == 20
        assert source_image.mime_type == "image/png"
        assert job.status == "queued"
        assert job.current_step == "validate_image"


def test_user_can_create_tool_with_initial_image_upload(client, app):
    register_and_login(client)
    image_bytes = BytesIO()
    Image.new("RGB", (20, 20), "white").save(image_bytes, format="PNG")
    image_bytes.seek(0)

    response = client.post(
        "/tools/new",
        data={
            "name": "Schraubendreher",
            "category_id": "0",
            "purpose": "Gridfinity-Einsatz",
            "image": (image_bytes, "schraubendreher.png"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Werkzeug wurde angelegt und das Bild wurde hochgeladen" in response.get_data(as_text=True)

    with app.app_context():
        tool = Tool.query.filter_by(name="Schraubendreher").one()
        source_image = SourceImage.query.filter_by(tool_id=tool.id).one()
        job = ProcessingJob.query.filter_by(tool_id=tool.id).one()
        assert source_image.original_filename == "schraubendreher.png"
        assert job.status == "queued"
