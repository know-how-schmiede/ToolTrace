from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from app.processing.mask_cleanup import MaskCleanupService

from .base import SegmentationBackend, SegmentationResult


class OpenCVSegmentationBackend(SegmentationBackend):
    def segment(self, image_path: str, output_path: str | Path | None = None) -> SegmentationResult:
        image = cv2.imread(str(image_path))
        if image is None:
            return SegmentationResult(confidence=0.0, warnings=["image_not_readable"])

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

        height, width = gray.shape[:2]
        background = self._estimate_background_lab(lab)
        color_distance = ((lab.astype("float32") - background.astype("float32")) ** 2).sum(axis=2) ** 0.5
        background_gray = float(background[0])

        dark_limit = min(195, max(150, int(background_gray - 28)))
        dark_mask = cv2.inRange(gray, 0, dark_limit)
        very_dark_mask = cv2.inRange(gray, 0, 155)
        color_mask = ((color_distance > 34) & (gray < 232)).astype("uint8") * 255
        saturation_mask = ((hsv[:, :, 1] > 60) & (gray < 238)).astype("uint8") * 255
        mask = cv2.bitwise_or(cv2.bitwise_or(dark_mask, very_dark_mask), cv2.bitwise_or(color_mask, saturation_mask))

        border = max(8, int(min(width, height) * 0.04))
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

    def _estimate_background_lab(self, lab_image) -> np.ndarray:
        height, width = lab_image.shape[:2]
        margin = max(10, int(min(width, height) * 0.08))
        samples = [
            lab_image[margin : height - margin, margin : margin * 2].reshape(-1, 3),
            lab_image[margin : height - margin, width - margin * 2 : width - margin].reshape(-1, 3),
            lab_image[margin : margin * 2, margin : width - margin].reshape(-1, 3),
            lab_image[height - margin * 2 : height - margin, margin : width - margin].reshape(-1, 3),
        ]
        return np.median(np.concatenate(samples), axis=0)
