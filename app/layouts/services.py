from __future__ import annotations

from app.layouts.gridfinity import calculate_gridfinity_size


class LayoutService:
    def calculate_gridfinity_layout(self, width_mm: float, height_mm: float, unit_mm: float = 42) -> dict:
        grid_x, grid_y, output_width, output_height = calculate_gridfinity_size(width_mm, height_mm, unit_mm)
        return {
            "grid_size_x": grid_x,
            "grid_size_y": grid_y,
            "width_mm": output_width,
            "height_mm": output_height,
            "grid_unit_mm": unit_mm,
        }
