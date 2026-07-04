from __future__ import annotations

from pathlib import Path

import cv2

from app.processing.perspective import PerspectiveCorrectionService
from tests.integration.test_tools import make_page_image_bytes


def test_perspective_correction_warps_page_to_a4_portrait(tmp_path: Path):
    source_path = tmp_path / "source.png"
    output_path = tmp_path / "corrected.png"
    source_path.write_bytes(make_page_image_bytes().getvalue())

    result = PerspectiveCorrectionService().correct(
        source_path,
        [(230, 60), (570, 60), (570, 540), (230, 540)],
        output_path,
        pixels_per_mm=2,
    )

    corrected = cv2.imread(str(output_path))
    assert output_path.exists()
    assert result.width_px == 420
    assert result.height_px == 594
    assert corrected.shape[:2] == (594, 420)
