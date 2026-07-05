from __future__ import annotations

from dataclasses import dataclass
import math
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
        aligned_output_path: str | Path | None = None,
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

        normalized = self._normalize_outer_contour(outer_contour, pixels_per_mm)
        if aligned_output_path is not None:
            self._write_aligned_preview(
                normalized["points_px"],
                normalized["width_px"],
                normalized["height_px"],
                aligned_output_path,
            )

        return ContourExtractionResult(
            geometry_data=normalized["geometry_data"],
            width_px=int(round(normalized["width_px"])),
            height_px=int(round(normalized["height_px"])),
            area_px=area_px,
            perimeter_px=perimeter_px,
            width_mm=normalized["width_mm"],
            height_mm=normalized["height_mm"],
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

    def manual_align_geometry(
        self,
        geometry_data: dict,
        *,
        edge_start: tuple[float, float],
        edge_end: tuple[float, float],
        grid_size_mm: float | None = None,
    ) -> dict:
        points_mm = np.array(geometry_data.get("points_mm") or [], dtype="float32")
        if len(points_mm) < 3:
            raise ValueError("contour_points_required")

        dx = edge_end[0] - edge_start[0]
        dy = edge_end[1] - edge_start[1]
        if math.hypot(dx, dy) <= 0.001:
            raise ValueError("alignment_edge_required")

        angle_rad = math.atan2(dy, dx)
        rotation_rad = -angle_rad
        cos_angle = math.cos(rotation_rad)
        sin_angle = math.sin(rotation_rad)
        rotation = np.array(
            [
                [cos_angle, -sin_angle],
                [sin_angle, cos_angle],
            ],
            dtype="float32",
        )

        rotated_points = points_mm @ rotation.T
        min_x = float(rotated_points[:, 0].min())
        min_y = float(rotated_points[:, 1].min())
        normalized_points = np.column_stack(
            [
                rotated_points[:, 0] - min_x,
                rotated_points[:, 1] - min_y,
            ]
        )
        width_mm = float(normalized_points[:, 0].max())
        height_mm = float(normalized_points[:, 1].max())
        normalized_points_mm = [
            [round(float(x), 3), round(float(y), 3)]
            for x, y in normalized_points
        ]

        updated = dict(geometry_data)
        updated["points_mm"] = normalized_points_mm
        updated["alignment"] = {
            "method": "user_selected_edge",
            "source_angle_deg": round(math.degrees(angle_rad), 3),
            "rotation_deg": round(math.degrees(rotation_rad), 3),
            "edge_start_mm": [round(float(edge_start[0]), 3), round(float(edge_start[1]), 3)],
            "edge_end_mm": [round(float(edge_end[0]), 3), round(float(edge_end[1]), 3)],
        }
        updated["bounding_box_mm"] = {
            "x": 0.0,
            "y": 0.0,
            "width": round(width_mm, 3),
            "height": round(height_mm, 3),
        }
        updated["source_alignment"] = geometry_data.get("alignment")
        if grid_size_mm and grid_size_mm > 0:
            updated["raster_bounding_box_mm"] = {
                "grid_size": round(float(grid_size_mm), 3),
                "width": round(math.ceil(width_mm / grid_size_mm) * grid_size_mm, 3),
                "height": round(math.ceil(height_mm / grid_size_mm) * grid_size_mm, 3),
            }
        else:
            updated.pop("raster_bounding_box_mm", None)
        return updated

    def smooth_geometry(
        self,
        geometry_data: dict,
        *,
        smoothing_level: int = 0,
        simplification_tolerance_mm: float = 0.0,
    ) -> dict:
        points_mm = np.array(geometry_data.get("points_mm") or [], dtype="float32")
        if len(points_mm) < 3:
            raise ValueError("contour_points_required")
        if smoothing_level < 0 or smoothing_level > 4:
            raise ValueError("smoothing_level_invalid")
        if simplification_tolerance_mm < 0 or simplification_tolerance_mm > 10:
            raise ValueError("simplification_tolerance_invalid")

        edited_points = points_mm
        for _ in range(smoothing_level):
            edited_points = self._chaikin_closed(edited_points)

        if simplification_tolerance_mm > 0:
            contour = edited_points.reshape((-1, 1, 2)).astype("float32")
            simplified = cv2.approxPolyDP(contour, simplification_tolerance_mm, True)
            if len(simplified) >= 3:
                edited_points = simplified.reshape(-1, 2).astype("float32")

        normalized_points, width_mm, height_mm = self._normalize_points_mm(edited_points)
        updated = dict(geometry_data)
        updated["points_mm"] = [
            [round(float(x), 3), round(float(y), 3)]
            for x, y in normalized_points
        ]
        updated["bounding_box_mm"] = {
            "x": 0.0,
            "y": 0.0,
            "width": round(width_mm, 3),
            "height": round(height_mm, 3),
        }
        updated["smoothing"] = {
            "method": "chaikin_and_douglas_peucker",
            "level": smoothing_level,
            "simplification_tolerance_mm": round(float(simplification_tolerance_mm), 3),
            "source_point_count": int(len(points_mm)),
            "result_point_count": int(len(normalized_points)),
        }
        updated["source_smoothing"] = geometry_data.get("smoothing")
        updated.pop("raster_bounding_box_mm", None)
        return updated

    def write_geometry_preview(
        self,
        geometry_data: dict,
        output_path: str | Path,
        *,
        pixels_per_mm: float = 6.0,
    ) -> tuple[int, int]:
        points_mm = np.array(geometry_data.get("points_mm") or [], dtype="float32")
        bounding_box = geometry_data.get("bounding_box_mm") or {}
        width_mm = float(bounding_box.get("width") or 0)
        height_mm = float(bounding_box.get("height") or 0)
        if len(points_mm) < 3 or width_mm <= 0 or height_mm <= 0:
            raise ValueError("contour_preview_points_required")

        points_px = points_mm * pixels_per_mm
        width_px = width_mm * pixels_per_mm
        height_px = height_mm * pixels_per_mm
        self._write_aligned_preview(points_px, width_px, height_px, output_path)
        image = cv2.imread(str(output_path))
        if image is None:
            raise ValueError("contour_preview_not_written")
        return image.shape[1], image.shape[0]

    def _chaikin_closed(self, points: np.ndarray) -> np.ndarray:
        smoothed = []
        for index, current in enumerate(points):
            next_point = points[(index + 1) % len(points)]
            smoothed.append(current * 0.75 + next_point * 0.25)
            smoothed.append(current * 0.25 + next_point * 0.75)
        return np.array(smoothed, dtype="float32")

    def _normalize_points_mm(self, points: np.ndarray) -> tuple[np.ndarray, float, float]:
        min_x = float(points[:, 0].min())
        min_y = float(points[:, 1].min())
        normalized = np.column_stack(
            [
                points[:, 0] - min_x,
                points[:, 1] - min_y,
            ]
        ).astype("float32")
        width_mm = float(normalized[:, 0].max())
        height_mm = float(normalized[:, 1].max())
        return normalized, width_mm, height_mm

    def _normalize_outer_contour(self, contour: np.ndarray, pixels_per_mm: float) -> dict:
        points = contour.reshape(-1, 2).astype("float32")
        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect).astype("float32")
        edges = [(box[(index + 1) % 4] - box[index]) for index in range(4)]
        longest_edge = max(edges, key=lambda edge: float(np.linalg.norm(edge)))
        angle_deg = float(np.degrees(np.arctan2(longest_edge[1], longest_edge[0])))
        rotation = cv2.getRotationMatrix2D(rect[0], angle_deg, 1.0)

        homogeneous_points = np.column_stack([points, np.ones(len(points), dtype="float32")])
        rotated_points = homogeneous_points @ rotation.T
        min_x = float(rotated_points[:, 0].min())
        max_x = float(rotated_points[:, 0].max())
        min_y = float(rotated_points[:, 1].min())
        max_y = float(rotated_points[:, 1].max())
        width_px = max_x - min_x
        height_px = max_y - min_y

        normalized_points_px = np.column_stack(
            [
                rotated_points[:, 0] - min_x,
                max_y - rotated_points[:, 1],
            ]
        )
        normalized_points_mm = normalized_points_px / pixels_per_mm
        points_mm = [
            [round(float(x), 3), round(float(y), 3)]
            for x, y in normalized_points_mm
        ]

        geometry_data = {
            "type": "outer_contour",
            "coordinate_space": "tool_mm",
            "origin": "bottom_left",
            "axis": {"x": "right", "y": "up"},
            "alignment": {
                "method": "min_area_rect_long_axis",
                "source_angle_deg": round(angle_deg, 3),
            },
            "points_mm": points_mm,
            "bounding_box_mm": {
                "x": 0.0,
                "y": 0.0,
                "width": round(width_px / pixels_per_mm, 3),
                "height": round(height_px / pixels_per_mm, 3),
            },
            "source_contour_px": {
                "coordinate_space": "perspective_corrected_px",
                "points": points.astype(int).tolist(),
            },
        }

        return {
            "geometry_data": geometry_data,
            "width_px": width_px,
            "height_px": height_px,
            "width_mm": width_px / pixels_per_mm,
            "height_mm": height_px / pixels_per_mm,
            "points_px": normalized_points_px,
        }

    def _write_aligned_preview(
        self,
        points_px: np.ndarray,
        width_px: float,
        height_px: float,
        output_path: str | Path,
    ) -> None:
        margin = 32
        max_preview_side = 720
        scale = min(max_preview_side / max(width_px, 1.0), max_preview_side / max(height_px, 1.0))
        scale = max(0.5, min(scale, 6.0))
        canvas_width = int(round(width_px * scale)) + margin * 2
        canvas_height = int(round(height_px * scale)) + margin * 2
        canvas = np.full((canvas_height, canvas_width, 3), 255, dtype=np.uint8)

        preview_points = np.column_stack(
            [
                margin + points_px[:, 0] * scale,
                margin + (height_px - points_px[:, 1]) * scale,
            ]
        ).round().astype("int32")
        bbox_top_left = (margin, margin)
        bbox_bottom_right = (
            margin + int(round(width_px * scale)),
            margin + int(round(height_px * scale)),
        )

        fill_layer = canvas.copy()
        cv2.fillPoly(fill_layer, [preview_points], (0, 0, 255))
        canvas = cv2.addWeighted(fill_layer, 0.30, canvas, 0.70, 0)
        cv2.polylines(canvas, [preview_points], True, (0, 0, 180), 2, cv2.LINE_AA)
        cv2.rectangle(canvas, bbox_top_left, bbox_bottom_right, (255, 90, 0), 2, cv2.LINE_AA)

        origin = (margin, bbox_bottom_right[1])
        x_axis_end = (bbox_bottom_right[0], bbox_bottom_right[1])
        y_axis_end = (margin, margin)
        cv2.arrowedLine(canvas, origin, x_axis_end, (0, 150, 0), 2, cv2.LINE_AA, tipLength=0.04)
        cv2.arrowedLine(canvas, origin, y_axis_end, (0, 150, 0), 2, cv2.LINE_AA, tipLength=0.04)
        cv2.circle(canvas, origin, 5, (0, 120, 0), -1)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), canvas)
