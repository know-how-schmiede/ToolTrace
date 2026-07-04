from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass
class ContourExtractionResult:
    geometry_data: dict
    width_px: int
    height_px: int
    area_px: float
    perimeter_px: float
    width_mm: float
    height_mm: float
    area_mm2: float
    perimeter_mm: float
    warnings: list[str]


class ContourExtractionService:
    def extract_outer_contour_overlay(
        self,
        *,
        image_path: str | Path,
        mask_path: str | Path,
        output_path: str | Path,
        pixels_per_mm: float,
    ) -> ContourExtractionResult:
        image = cv2.imread(str(image_path))
        mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
        if image is None:
            return self._empty_result(["image_not_readable"])
        if mask is None:
            return self._empty_result(["mask_not_readable"])

        binary = np.where(mask > 0, 255, 0).astype("uint8")
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return self._empty_result(["outer_contour_not_found"])

        outer_contour = max(contours, key=cv2.contourArea)
        area_px = float(cv2.contourArea(outer_contour))
        perimeter_px = float(cv2.arcLength(outer_contour, True))
        if area_px <= 0 or perimeter_px <= 0:
            return self._empty_result(["outer_contour_not_found"])

        filled_contour = np.zeros_like(binary)
        cv2.fillPoly(filled_contour, [outer_contour], 255)
        overlay = image.copy()
        overlay[filled_contour > 0] = (0, 0, 255)
        blended = image.copy()
        blended[filled_contour > 0] = cv2.addWeighted(overlay, 0.30, image, 0.70, 0)[filled_contour > 0]

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), blended)

        x, y, width_px, height_px = cv2.boundingRect(outer_contour)
        points = outer_contour.reshape(-1, 2).astype(int).tolist()
        geometry_data = {
            "type": "outer_contour",
            "coordinate_space": "perspective_corrected_px",
            "points": points,
            "bounding_box_px": {"x": int(x), "y": int(y), "width": int(width_px), "height": int(height_px)},
        }

        return ContourExtractionResult(
            geometry_data=geometry_data,
            width_px=int(width_px),
            height_px=int(height_px),
            area_px=area_px,
            perimeter_px=perimeter_px,
            width_mm=width_px / pixels_per_mm,
            height_mm=height_px / pixels_per_mm,
            area_mm2=area_px / (pixels_per_mm * pixels_per_mm),
            perimeter_mm=perimeter_px / pixels_per_mm,
            warnings=[],
        )

    def _empty_result(self, warnings: list[str]) -> ContourExtractionResult:
        return ContourExtractionResult(
            geometry_data={},
            width_px=0,
            height_px=0,
            area_px=0.0,
            perimeter_px=0.0,
            width_mm=0.0,
            height_mm=0.0,
            area_mm2=0.0,
            perimeter_mm=0.0,
            warnings=warnings,
        )
