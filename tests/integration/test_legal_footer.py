from version import VERSION


def test_public_index_shows_footer_version_and_legal_links(client):
    response = client.get("/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert f"ToolTrace v{VERSION}" in html
    assert "/impressum" in html
    assert "/datenschutz" in html


def test_legal_pages_are_public(client):
    impressum = client.get("/impressum")
    datenschutz = client.get("/datenschutz")

    assert impressum.status_code == 200
    assert "Impressum" in impressum.get_data(as_text=True)
    assert datenschutz.status_code == 200
    assert "Datenschutz" in datenschutz.get_data(as_text=True)
