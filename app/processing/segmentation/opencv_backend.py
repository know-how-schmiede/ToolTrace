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
        normalized_gray = self._normalize_illumination(gray)

        height, width = gray.shape[:2]
        background = self._estimate_background_lab(lab)
        lab_delta = lab.astype("float32") - background.astype("float32")
        color_distance = (lab_delta**2).sum(axis=2) ** 0.5
        chroma_distance = (lab_delta[:, :, 1:] ** 2).sum(axis=2) ** 0.5
        background_gray = float(background[0])
        normalized_background_gray = float(np.median(normalized_gray))

        dark_limit = min(198, max(152, int(normalized_background_gray - 28)))
        dark_mask = cv2.inRange(normalized_gray, 0, dark_limit)
        very_dark_mask = cv2.inRange(normalized_gray, 0, 158)
        color_mask = (
            ((color_distance > 38) | (chroma_distance > 16))
            & (normalized_gray < 235)
            & (gray < 242)
        ).astype("uint8") * 255
        saturation_mask = ((hsv[:, :, 1] > 60) & (normalized_gray < 240)).astype("uint8") * 255
        edge_supported_dark_mask = self._edge_supported_dark_mask(
            gray,
            normalized_gray,
            background_gray,
            normalized_background_gray,
        )
        mask = cv2.bitwise_or(
            cv2.bitwise_or(dark_mask, very_dark_mask),
            cv2.bitwise_or(cv2.bitwise_or(color_mask, saturation_mask), edge_supported_dark_mask),
        )

        border = max(8, int(min(width, height) * 0.04))
        mask[:border, :] = 0
        mask[-border:, :] = 0
        mask[:, :border] = 0
        mask[:, -border:] = 0
        mask = self._remove_page_edge_artifacts(mask)

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

    def _normalize_illumination(self, gray_image: np.ndarray) -> np.ndarray:
        height, width = gray_image.shape[:2]
        kernel_size = max(51, int(min(width, height) * 0.09))
        if kernel_size % 2 == 0:
            kernel_size += 1

        illumination = cv2.GaussianBlur(gray_image, (kernel_size, kernel_size), 0)
        illumination = np.maximum(illumination.astype("float32"), 1.0)
        target_gray = float(np.median(illumination))
        normalized = gray_image.astype("float32") / illumination * target_gray
        return np.clip(normalized, 0, 255).astype("uint8")

    def _edge_supported_dark_mask(
        self,
        gray_image: np.ndarray,
        normalized_gray_image: np.ndarray,
        background_gray: float,
        normalized_background_gray: float,
    ) -> np.ndarray:
        blurred = cv2.GaussianBlur(gray_image, (3, 3), 0)
        edges = cv2.Canny(blurred, 18, 60)
        edge_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
        edge_support = cv2.dilate(edges, edge_kernel, iterations=1)
        return (
            (gray_image < background_gray - 18)
            & (normalized_gray_image < normalized_background_gray + 18)
            & (edge_support > 0)
        ).astype("uint8") * 255

    def _remove_page_edge_artifacts(self, mask: np.ndarray) -> np.ndarray:
        filtered = np.where(mask > 0, 255, 0).astype("uint8")
        height, width = filtered.shape[:2]
        edge_margin = max(12, int(min(width, height) * 0.07))
        inner_margin = edge_margin * 2

        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(filtered, connectivity=8)
        for label in range(1, num_labels):
            x, y, component_width, component_height, area = stats[label]
            touches_page_edge = (
                x <= edge_margin
                or y <= edge_margin
                or x + component_width >= width - edge_margin
                or y + component_height >= height - edge_margin
            )
            if not touches_page_edge:
                continue

            reaches_inner_page = (
                x < width - inner_margin
                and x + component_width > inner_margin
                and y < height - inner_margin
                and y + component_height > inner_margin
            )
            fill_ratio = area / max(component_width * component_height, 1)
            elongated = max(component_width, component_height) / max(min(component_width, component_height), 1) > 5
            if not reaches_inner_page or (elongated and fill_ratio < 0.55):
                filtered[labels == label] = 0

        return filtered
