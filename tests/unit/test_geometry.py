from app.layouts.gridfinity import calculate_gridfinity_size
from app.processing.geometry import pixels_to_mm


def test_pixels_to_mm():
    assert pixels_to_mm(2100, 10) == 210


def test_gridfinity_size_rounds_up_to_full_units():
    assert calculate_gridfinity_size(108, 67, 42) == (3, 2, 126, 84)
