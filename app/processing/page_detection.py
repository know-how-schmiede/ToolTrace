from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np


@dataclass
class PageDetectionResult:
    found: bool
    corners: list[tuple[float, float]] = field(default_factory=list)
    score: float = 0.0
    warnings: list[str] = field(default_factory=list)
    preview_width_px: int | None = None
    preview_height_px: int | None = None


class PageDetectionService:
    expected_ratio = 210 / 297

    def detect(
        self,
        image_path: str | Path,
        expected_width_mm: float = 210.0,
        expected_height_mm: float = 297.0,
    ) -> PageDetectionResult:
        image = cv2.imread(str(image_path))
        if image is None:
            return PageDetectionResult(found=False, warnings=["image_not_readable"])

        height, width = image.shape[:2]
        scale = min(1.0, 1600 / max(width, height))
        analysis = image
        if scale < 1.0:
            analysis = cv2.resize(image, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_AREA)

        gray = cv2.cvtColor(analysis, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        best_quad = None
        best_score = 0.0
        analysis_area = analysis.shape[0] * analysis.shape[1]
        bright_candidate = self._detect_bright_background(blurred, analysis_area, expected_width_mm, expected_height_mm)
        if bright_candidate is not None:
            best_quad, best_score = bright_candidate

        edges = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < analysis_area * 0.08:
                continue
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
            if len(approx) != 4 or not cv2.isContourConvex(approx):
                continue

            points = approx.reshape(4, 2).astype("float32")
            ordered = self._order_points(points)
            ratio_score = self._ratio_score(ordered, expected_width_mm, expected_height_mm)
            area_score = min(1.0, area / (analysis_area * 0.65))
            score = ratio_score * 0.75 + area_score * 0.25
            if score > best_score:
                best_quad = ordered
                best_score = score

        if best_quad is None or best_score < 0.55:
            return PageDetectionResult(found=False, score=best_score, warnings=["page_not_found"])

        if scale != 1.0:
            best_quad = best_quad / scale

        corners = [(round(float(x), 2), round(float(y), 2)) for x, y in best_quad]
        return PageDetectionResult(found=True, corners=corners, score=round(float(best_score), 3))

    def write_preview(self, image_path: str | Path, result: PageDetectionResult, output_path: str | Path) -> tuple[int, int]:
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError("image_not_readable")

        if result.found and result.corners:
            points = np.array(result.corners, dtype=np.int32)
            overlay = image.copy()
            cv2.fillPoly(overlay, [points], (0, 180, 0))
            image = cv2.addWeighted(overlay, 0.30, image, 0.70, 0)
            cv2.polylines(image, [points], True, (0, 180, 0), 6)
            for index, point in enumerate(points, start=1):
                point_tuple = (int(point[0]), int(point[1]))
                cv2.circle(image, point_tuple, 12, (0, 90, 255), -1)
                cv2.putText(
                    image,
                    str(index),
                    (point_tuple[0] + 14, point_tuple[1] - 14),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 90, 255),
                    2,
                    cv2.LINE_AA,
                )
        else:
            cv2.putText(
                image,
                "Hintergrund nicht erkannt",
                (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (0, 0, 255),
                3,
                cv2.LINE_AA,
            )

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), image)
        return image.shape[1], image.shape[0]

    def _order_points(self, points: np.ndarray) -> np.ndarray:
        rect = np.zeros((4, 2), dtype="float32")
        point_sum = points.sum(axis=1)
        point_diff = np.diff(points, axis=1)
        rect[0] = points[np.argmin(point_sum)]
        rect[2] = points[np.argmax(point_sum)]
        rect[1] = points[np.argmin(point_diff)]
        rect[3] = points[np.argmax(point_diff)]
        return rect

    def _detect_bright_background(
        self,
        gray: np.ndarray,
        analysis_area: int,
        expected_width_mm: float,
        expected_height_mm: float,
    ) -> tuple[np.ndarray, float] | None:
        _, otsu_mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        high_percentile = np.percentile(gray, 82)
        threshold_value = max(80, min(245, high_percentile - 8))
        _, bright_mask = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
        mask = cv2.bitwise_or(otsu_mask, bright_mask)

        close_size = max(15, int(round(max(gray.shape[:2]) * 0.025)))
        if close_size % 2 == 0:
            close_size += 1
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (close_size, close_size))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), dtype=np.uint8))

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        best_quad = None
        best_score = 0.0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < analysis_area * 0.08 or area > analysis_area * 0.95:
                continue

            rect = cv2.minAreaRect(contour)
            box = cv2.boxPoints(rect).astype("float32")
            ordered = self._order_points(box)
            ratio_score = self._ratio_score(ordered, expected_width_mm, expected_height_mm)
            area_score = min(1.0, area / (analysis_area * 0.55))
            fill_score = min(1.0, area / max(cv2.contourArea(box), 1.0))
            score = ratio_score * 0.65 + area_score * 0.20 + fill_score * 0.15
            if score > best_score:
                best_quad = ordered
                best_score = score

        if best_quad is None or best_score < 0.55:
            return None
        return best_quad, best_score

    def _ratio_score(self, ordered_points: np.ndarray, expected_width_mm: float, expected_height_mm: float) -> float:
        top_width = np.linalg.norm(ordered_points[1] - ordered_points[0])
        bottom_width = np.linalg.norm(ordered_points[2] - ordered_points[3])
        left_height = np.linalg.norm(ordered_points[3] - ordered_points[0])
        right_height = np.linalg.norm(ordered_points[2] - ordered_points[1])
        page_width = max((top_width + bottom_width) / 2, 1)
        page_height = max((left_height + right_height) / 2, 1)
        ratio = min(page_width / page_height, page_height / page_width)
        expected_ratio = min(expected_width_mm / expected_height_mm, expected_height_mm / expected_width_mm)
        ratio_error = abs(ratio - expected_ratio)
        return max(0.0, 1.0 - ratio_error / 0.25)
