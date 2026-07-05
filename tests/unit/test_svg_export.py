from app.exports.svg_export import SvgExportService


def test_empty_layout_svg_uses_mm_dimensions():
    svg = SvgExportService().empty_layout_svg(width_mm=126, height_mm=84, label="Kombizange")

    assert 'width="126mm"' in svg
    assert 'height="84mm"' in svg
    assert 'viewBox="0 0 126 84"' in svg
    assert 'id="layout-border"' in svg


def test_contour_svg_exports_manual_align_coordinate_view():
    geometry_data = {
        "points_mm": [[0, 0], [20, 0], [20, 10], [0, 10]],
        "bounding_box_mm": {"x": 0, "y": 0, "width": 20, "height": 10},
    }

    svg = SvgExportService().contour_svg(geometry_data=geometry_data, label="Versatz")

    assert 'width="20mm"' in svg
    assert 'height="10mm"' in svg
    assert 'viewBox="0 0 20 10"' in svg
    assert 'id="manual-align-export"' in svg
    assert 'id="offset-contour"' in svg
    assert 'fill="none"' in svg
    assert 'stroke="#157347"' in svg
    assert 'd="M 0 10 L 20 10 L 20 0 L 0 0 Z"' in svg
