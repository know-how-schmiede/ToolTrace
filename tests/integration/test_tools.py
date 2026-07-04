from __future__ import annotations

from io import BytesIO

from PIL import Image

from app.models import ProcessingJob, SourceImage, Tool, User
from app.tools.services import ToolService
from tests.conftest import register_and_login


def test_user_can_create_tool(client, app):
    register_and_login(client)
    image_bytes = BytesIO()
    Image.new("RGB", (20, 20), "white").save(image_bytes, format="PNG")
    image_bytes.seek(0)

    response = client.post(
        "/tools/new",
        data={
            "name": "Kombizange",
            "category_id": "0",
            "purpose": "Schaumstoffeinlage",
            "manufacturer": "Knipex",
            "model": "Demo",
            "image": (image_bytes, "kombizange.png"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Kombizange" in response.get_data(as_text=True)

    with app.app_context():
        tool = Tool.query.filter_by(name="Kombizange").one()
        assert tool.status == "processing"
        assert tool.purpose == "Schaumstoffeinlage"


def test_image_upload_stores_metadata_and_placeholder_job(client, app):
    register_and_login(client)
    with app.app_context():
        user = User.query.filter_by(email="user@example.com").one()
        tool = ToolService().create_tool(user.id, {"name": "Hammer", "purpose": "Shadowboard"})
        tool_id = tool.id

    image_bytes = BytesIO()
    Image.new("RGB", (20, 20), "white").save(image_bytes, format="PNG")
    image_bytes.seek(0)

    response = client.post(
        f"/tools/{tool_id}",
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


def test_tool_library_renders_thumbnail_and_image_route(client, app):
    register_and_login(client)
    image_bytes = BytesIO()
    Image.new("RGB", (20, 20), "white").save(image_bytes, format="PNG")
    image_bytes.seek(0)

    client.post(
        "/tools/new",
        data={
            "name": "Thumbnail-Test",
            "category_id": "0",
            "image": (image_bytes, "thumbnail.png"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    with app.app_context():
        tool = Tool.query.filter_by(name="Thumbnail-Test").one()
        source_image = SourceImage.query.filter_by(tool_id=tool.id).one()

    index_response = client.get("/tools/")
    image_url = f"/tools/{tool.id}/images/{source_image.id}"
    assert index_response.status_code == 200
    assert image_url in index_response.get_data(as_text=True)

    image_response = client.get(image_url)
    assert image_response.status_code == 200
    assert image_response.mimetype == "image/png"


def test_small_image_upload_is_saved_with_warning(client, app):
    app.config["MIN_IMAGE_WIDTH"] = 1200
    app.config["MIN_IMAGE_HEIGHT"] = 1200
    register_and_login(client)
    image_bytes = BytesIO()
    Image.new("RGB", (1, 1), "white").save(image_bytes, format="PNG")
    image_bytes.seek(0)

    response = client.post(
        "/tools/new",
        data={
            "name": "Mini",
            "category_id": "0",
            "purpose": "Upload-Test",
            "image": (image_bytes, "mini.png"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "kleiner als die empfohlene Mindestaufloesung" in html
    assert "Werkzeug wurde angelegt und das Bild wurde hochgeladen" in html

    with app.app_context():
        source_image = SourceImage.query.filter_by(original_filename="mini.png").one()
        assert source_image.width_px == 1


def test_photo_is_the_only_required_field_for_new_tool(client, app):
    register_and_login(client)
    image_bytes = BytesIO()
    Image.new("RGB", (20, 20), "white").save(image_bytes, format="PNG")
    image_bytes.seek(0)

    response = client.post(
        "/tools/new",
        data={
            "category_id": "0",
            "image": (image_bytes, "nur-foto.png"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Werkzeug wurde angelegt und das Bild wurde hochgeladen" in html

    with app.app_context():
        tool = Tool.query.filter_by(name="nur-foto").one()
        source_image = SourceImage.query.filter_by(tool_id=tool.id).one()
        assert tool.purpose == ""
        assert source_image.original_filename == "nur-foto.png"


def test_invalid_required_photo_does_not_create_tool(client, app):
    register_and_login(client)

    response = client.post(
        "/tools/new",
        data={
            "name": "Defekt",
            "category_id": "0",
            "image": (BytesIO(b"not an image"), "defekt.png"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Das Werkzeug wurde nicht gespeichert" in html

    with app.app_context():
        assert Tool.query.filter_by(name="Defekt").count() == 0
