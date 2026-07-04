from __future__ import annotations

from pathlib import Path

import cv2

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
