from __future__ import annotations

from pathlib import Path

import cv2
from PIL import Image, ImageDraw

from app.processing.perspective import PerspectiveCorrectionService
from app.processing.segmentation.opencv_backend import OpenCVSegmentationBackend
from tests.integration.test_tools import make_page_image_bytes


def test_opencv_segmentation_extracts_dark_tool_on_white_page(tmp_path: Path):
    source_path = tmp_path / "source.png"
    corrected_path = tmp_path / "corrected.png"
    mask_path = tmp_path / "mask.png"
    source_path.write_bytes(make_page_image_bytes().getvalue())

    PerspectiveCorrectionService().correct(
        source_path,
        [(230, 60), (570, 60), (570, 540), (230, 540)],
        corrected_path,
        pixels_per_mm=2,
    )
    result = OpenCVSegmentationBackend().segment(corrected_path, mask_path)

    mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
    assert mask_path.exists()
    assert result.confidence and result.confidence > 0
    assert result.foreground_area_px > 0
    assert mask.max() == 255


def test_opencv_segmentation_keeps_low_quality_screwdriver_shaft(tmp_path: Path):
    image_path = tmp_path / "screwdriver.png"
    mask_path = tmp_path / "screwdriver-mask.png"
    image = Image.new("RGB", (420, 594), (214, 211, 204))
    draw = ImageDraw.Draw(image)

    draw.line((160, 135, 268, 365), fill=(190, 188, 181), width=18)
    draw.line((150, 125, 255, 355), fill=(175, 172, 165), width=8)
    draw.line((145, 118, 250, 348), fill=(92, 92, 86), width=5)
    draw.ellipse((220, 330, 315, 510), fill=(25, 24, 22))
    draw.rectangle((238, 340, 285, 385), fill=(158, 122, 57))
    image.save(image_path)

    result = OpenCVSegmentationBackend().segment(image_path, mask_path)
    mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)

    assert result.foreground_area_px > 0
    assert mask[180, 170] == 255
    assert mask[440, 270] == 255
