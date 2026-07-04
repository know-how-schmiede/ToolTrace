from __future__ import annotations

import cv2
import numpy as np


class MaskCleanupService:
    def clean(self, mask: np.ndarray) -> tuple[np.ndarray, int]:
        if mask.ndim != 2:
            raise ValueError("binary_mask_required")

        binary = np.where(mask > 0, 255, 0).astype("uint8")
        close_kernel = np.ones((5, 5), np.uint8)
        open_kernel = np.ones((3, 3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, close_kernel, iterations=1)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, open_kernel, iterations=1)

        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
        if num_labels <= 1:
            return np.zeros_like(binary), 0

        height, width = binary.shape[:2]
        image_area = height * width
        edge_margin = max(8, int(min(width, height) * 0.025))
        minimum_area = max(250, int(image_area * 0.00035))
        maximum_area = int(image_area * 0.45)

        candidates: list[tuple[int, int]] = []
        for label in range(1, num_labels):
            x, y, component_width, component_height, area = stats[label]
            if area < minimum_area or area > maximum_area:
                continue
            touches_edge = (
                x <= edge_margin
                or y <= edge_margin
                or x + component_width >= width - edge_margin
                or y + component_height >= height - edge_margin
            )
            if touches_edge:
                continue
            candidates.append((label, int(area)))

        if not candidates:
            return np.zeros_like(binary), 0

        largest_area = max(area for _, area in candidates)
        cleaned = np.zeros_like(binary)
        kept_area = 0
        for label, area in candidates:
            if area >= max(minimum_area, largest_area * 0.04):
                cleaned[labels == label] = 255
                kept_area += area

        return cleaned, kept_area
