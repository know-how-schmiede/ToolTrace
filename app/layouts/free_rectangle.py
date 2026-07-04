def calculate_free_rectangle(
    contour_width_mm: float,
    contour_height_mm: float,
    margin_left_mm: float,
    margin_right_mm: float,
    margin_top_mm: float,
    margin_bottom_mm: float,
) -> tuple[float, float]:
    return (
        contour_width_mm + margin_left_mm + margin_right_mm,
        contour_height_mm + margin_top_mm + margin_bottom_mm,
    )
