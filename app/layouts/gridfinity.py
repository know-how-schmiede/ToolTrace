from __future__ import annotations

from math import ceil


def calculate_gridfinity_size(width_mm: float, height_mm: float, unit_mm: float) -> tuple[int, int, float, float]:
    grid_x = max(1, ceil(width_mm / unit_mm))
    grid_y = max(1, ceil(height_mm / unit_mm))
    return grid_x, grid_y, grid_x * unit_mm, grid_y * unit_mm
