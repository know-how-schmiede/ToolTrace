from __future__ import annotations

import cv2
import numpy as np


class MaskCleanupService:
    def clean(self, mask: np.ndarray) -> tuple[np.ndarray, int]:
        if mask.ndim != 2:
            raise ValueError("binary_mask_required")

        binary = np.where(mask > 0, 255, 0).astype("uint8")
        kernel = np.ones((7, 7), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)

        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
        if num_labels <= 1:
            return np.zeros_like(binary), 0

        largest_label = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        cleaned = np.where(labels == largest_label, 255, 0).astype("uint8")
        return cleaned, int(stats[largest_label, cv2.CC_STAT_AREA])
