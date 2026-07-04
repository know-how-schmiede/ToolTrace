from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass
class PerspectiveCorrectionResult:
    width_px: int
    height_px: int
    width_mm: float
    height_mm: float
    pixels_per_mm: float


class PerspectiveCorrectionService:
    portrait_width_mm = 210.0
    portrait_height_mm = 297.0

    def correct(
        self,
        image_path: str | Path,
        page_corners: list[tuple[float, float]],
        output_path: str | Path,
        pixels_per_mm: float,
    ) -> PerspectiveCorrectionResult:
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError("image_not_readable")
        if len(page_corners) != 4:
            raise ValueError("page_corners_required")

        source_points = np.array(page_corners, dtype="float32")
        page_width_px = max(
            np.linalg.norm(source_points[1] - source_points[0]),
            np.linalg.norm(source_points[2] - source_points[3]),
        )
        page_height_px = max(
            np.linalg.norm(source_points[3] - source_points[0]),
            np.linalg.norm(source_points[2] - source_points[1]),
        )

        if page_width_px > page_height_px:
            output_width_mm = self.portrait_height_mm
            output_height_mm = self.portrait_width_mm
        else:
            output_width_mm = self.portrait_width_mm
            output_height_mm = self.portrait_height_mm

        output_width_px = int(round(output_width_mm * pixels_per_mm))
        output_height_px = int(round(output_height_mm * pixels_per_mm))
        destination_points = np.array(
            [
                [0, 0],
                [output_width_px - 1, 0],
                [output_width_px - 1, output_height_px - 1],
                [0, output_height_px - 1],
            ],
            dtype="float32",
        )

        transform = cv2.getPerspectiveTransform(source_points, destination_points)
        corrected = cv2.warpPerspective(image, transform, (output_width_px, output_height_px))

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), corrected)

        return PerspectiveCorrectionResult(
            width_px=output_width_px,
            height_px=output_height_px,
            width_mm=output_width_mm,
            height_mm=output_height_mm,
            pixels_per_mm=pixels_per_mm,
        )
