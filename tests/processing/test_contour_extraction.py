from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from app.processing.contour_extraction import ContourExtractionService


def test_outer_contour_overlay_ignores_inner_artifacts(tmp_path: Path):
    image_path = tmp_path / "image.png"
    mask_path = tmp_path / "mask.png"
    overlay_path = tmp_path / "overlay.png"

    image = np.full((100, 140, 3), 200, dtype=np.uint8)
    mask = np.zeros((100, 140), dtype=np.uint8)
    cv2.rectangle(mask, (35, 25), (105, 80), 255, -1)
    cv2.circle(mask, (70, 52), 12, 0, -1)
    cv2.rectangle(mask, (5, 5), (12, 12), 255, -1)
    cv2.imwrite(str(image_path), image)
    cv2.imwrite(str(mask_path), mask)

    result = ContourExtractionService().extract_outer_contour_overlay(
        image_path=image_path,
        mask_path=mask_path,
        output_path=overlay_path,
        pixels_per_mm=2,
    )
    overlay = cv2.imread(str(overlay_path))

    assert result.warnings == []
    assert result.geometry_data["type"] == "outer_contour"
    assert result.width_mm > 30
    assert overlay[52, 70, 2] > overlay[52, 70, 0]
    assert overlay[8, 8].tolist() == [200, 200, 200]
