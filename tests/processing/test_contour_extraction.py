from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from app.processing.contour_extraction import ContourExtractionService


def test_outer_contour_overlay_ignores_inner_artifacts(tmp_path: Path):
    image_path = tmp_path / "image.png"
    mask_path = tmp_path / "mask.png"
    overlay_path = tmp_path / "overlay.png"
    aligned_path = tmp_path / "aligned.png"

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
        aligned_output_path=aligned_path,
    )
    overlay = cv2.imread(str(overlay_path))
    aligned = cv2.imread(str(aligned_path))

    assert result.warnings == []
    assert result.geometry_data["type"] == "outer_contour"
    assert result.geometry_data["coordinate_space"] == "tool_mm"
    assert result.geometry_data["origin"] == "bottom_left"
    assert result.geometry_data["bounding_box_mm"]["x"] == 0.0
    assert result.geometry_data["bounding_box_mm"]["y"] == 0.0
    assert result.width_mm > 30
    assert min(point[0] for point in result.geometry_data["points_mm"]) >= 0
    assert min(point[1] for point in result.geometry_data["points_mm"]) >= 0
    assert overlay[52, 70, 2] > overlay[52, 70, 0]
    assert overlay[8, 8].tolist() == [200, 200, 200]
    assert aligned is not None
    assert ((aligned[:, :, 2] > 200) & (aligned[:, :, 0] < 230)).any()


def test_outer_contour_geometry_aligns_long_axis_to_x(tmp_path: Path):
    image_path = tmp_path / "rotated-image.png"
    mask_path = tmp_path / "rotated-mask.png"
    overlay_path = tmp_path / "rotated-overlay.png"

    image = np.full((160, 160, 3), 220, dtype=np.uint8)
    mask = np.zeros((160, 160), dtype=np.uint8)
    box = cv2.boxPoints(((80, 80), (95, 24), 35)).astype(int)
    cv2.fillPoly(mask, [box], 255)
    cv2.imwrite(str(image_path), image)
    cv2.imwrite(str(mask_path), mask)

    result = ContourExtractionService().extract_outer_contour_overlay(
        image_path=image_path,
        mask_path=mask_path,
        output_path=overlay_path,
        pixels_per_mm=2,
    )

    assert result.warnings == []
    assert result.width_mm > result.height_mm
    assert result.geometry_data["bounding_box_mm"]["width"] > result.geometry_data["bounding_box_mm"]["height"]
    assert min(point[0] for point in result.geometry_data["points_mm"]) >= 0
    assert min(point[1] for point in result.geometry_data["points_mm"]) >= 0


def test_manual_alignment_rotates_selected_edge_to_x_axis():
    geometry_data = {
        "type": "outer_contour",
        "coordinate_space": "tool_mm",
        "origin": "bottom_left",
        "axis": {"x": "right", "y": "up"},
        "points_mm": [[0, 0], [10, 0], [10, 30], [0, 30]],
        "bounding_box_mm": {"x": 0, "y": 0, "width": 10, "height": 30},
        "alignment": {"method": "min_area_rect_long_axis"},
    }

    aligned = ContourExtractionService().manual_align_geometry(
        geometry_data,
        edge_start=(0, 0),
        edge_end=(0, 30),
        grid_size_mm=20,
    )

    assert aligned["alignment"]["method"] == "user_selected_edge"
    assert aligned["bounding_box_mm"]["width"] == 30
    assert aligned["bounding_box_mm"]["height"] == 10
    assert aligned["raster_bounding_box_mm"]["width"] == 40
    assert aligned["raster_bounding_box_mm"]["height"] == 20
    assert min(point[0] for point in aligned["points_mm"]) == 0
    assert min(point[1] for point in aligned["points_mm"]) == 0
