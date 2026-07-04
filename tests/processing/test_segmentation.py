from __future__ import annotations

from pathlib import Path

import cv2

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
