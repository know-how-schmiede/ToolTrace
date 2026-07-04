from app.models import User

from tests.conftest import register_and_login


def test_user_can_register_and_reach_dashboard(client, app):
    response = register_and_login(client)

    assert response.status_code == 200
    assert "Dashboard" in response.get_data(as_text=True)

    with app.app_context():
        user = User.query.filter_by(email="user@example.com").one()
        assert user.check_password("password123")
