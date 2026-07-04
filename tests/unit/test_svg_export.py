from app.exports.svg_export import SvgExportService


def test_empty_layout_svg_uses_mm_dimensions():
    svg = SvgExportService().empty_layout_svg(width_mm=126, height_mm=84, label="Kombizange")

    assert 'width="126mm"' in svg
    assert 'height="84mm"' in svg
    assert 'viewBox="0 0 126 84"' in svg
    assert 'id="layout-border"' in svg
