from __future__ import annotations

from pathlib import Path

import cv2
from PIL import Image, ImageDraw

from app.processing.page_detection import PageDetectionResult, PageDetectionService
from tests.integration.test_tools import make_page_image_bytes


def test_page_detection_preview_adds_transparent_green_fill(tmp_path: Path):
    image_path = tmp_path / "source.png"
    preview_path = tmp_path / "preview.png"
    image_path.write_bytes(make_page_image_bytes().getvalue())

    result = PageDetectionResult(
        found=True,
        corners=[(230, 60), (570, 60), (570, 540), (230, 540)],
        score=1.0,
    )

    PageDetectionService().write_preview(image_path, result, preview_path)

    preview = cv2.imread(str(preview_path))
    original = cv2.imread(str(image_path))
    preview_pixel = preview[100, 300]
    original_pixel = original[100, 300]

    assert preview_pixel[1] > preview_pixel[0]
    assert preview_pixel[1] > preview_pixel[2]
    assert preview_pixel[1] < original_pixel[1]


def test_page_detection_uses_bright_light_table_area_in_underexposed_photo(tmp_path: Path):
    image_path = tmp_path / "light-table.png"
    image = Image.new("RGB", (1000, 750), "#21160f")
    draw = ImageDraw.Draw(image)
    draw.rectangle((250, 175, 820, 575), fill="#f2f4f8")
    draw.rectangle((420, 320, 610, 375), fill="#2a1010")
    draw.rectangle((590, 300, 665, 425), fill="#111111")
    image.save(image_path)

    result = PageDetectionService().detect(
        image_path,
        expected_width_mm=313.0,
        expected_height_mm=215.0,
    )

    assert result.found
    assert result.score >= 0.55
    assert len(result.corners) == 4
    top_left, top_right, bottom_right, bottom_left = result.corners
    assert 230 <= top_left[0] <= 270
    assert 155 <= top_left[1] <= 195
    assert 800 <= bottom_right[0] <= 840
    assert 555 <= bottom_right[1] <= 595
    assert top_right[0] > top_left[0]
    assert bottom_left[1] > top_left[1]
