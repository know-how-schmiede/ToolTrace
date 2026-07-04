from __future__ import annotations

from pathlib import Path

import cv2

from app.processing.mask_cleanup import MaskCleanupService

from .base import SegmentationBackend, SegmentationResult


class OpenCVSegmentationBackend(SegmentationBackend):
    def segment(self, image_path: str, output_path: str | Path | None = None) -> SegmentationResult:
        image = cv2.imread(str(image_path))
        if image is None:
            return SegmentationResult(confidence=0.0, warnings=["image_not_readable"])

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        dark_mask = cv2.inRange(gray, 0, 215)
        saturation_mask = cv2.inRange(hsv[:, :, 1], 35, 255)
        mask = cv2.bitwise_or(dark_mask, saturation_mask)

        height, width = mask.shape[:2]
        border = max(4, int(min(width, height) * 0.01))
        mask[:border, :] = 0
        mask[-border:, :] = 0
        mask[:, :border] = 0
        mask[:, -border:] = 0

        cleaned, foreground_area = MaskCleanupService().clean(mask)
        image_area = width * height
        warnings: list[str] = []
        if foreground_area == 0:
            warnings.append("tool_not_found")
        if foreground_area > image_area * 0.75:
            warnings.append("segmentation_area_too_large")

        confidence = min(1.0, foreground_area / max(image_area * 0.08, 1))
        if output_path is not None:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(output_path), cleaned)

        return SegmentationResult(
            mask_path=str(output_path) if output_path is not None else None,
            confidence=round(float(confidence), 3),
            warnings=warnings,
            width_px=width,
            height_px=height,
            foreground_area_px=foreground_area,
        )
