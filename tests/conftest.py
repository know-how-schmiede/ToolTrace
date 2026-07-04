from __future__ import annotations

import shutil

import pytest

from app import create_app
from app.config import TestConfig
from app.extensions import db


@pytest.fixture()
def app():
    if TestConfig.STORAGE_PATH.exists():
        shutil.rmtree(TestConfig.STORAGE_PATH)
    test_app = create_app(TestConfig)
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()
    if TestConfig.STORAGE_PATH.exists():
        shutil.rmtree(TestConfig.STORAGE_PATH)


@pytest.fixture()
def client(app):
    return app.test_client()


def register_and_login(client, email: str = "user@example.com", username: str = "user"):
    return client.post(
        "/register",
        data={
            "email": email,
            "username": username,
            "first_name": "Test",
            "last_name": "User",
            "password": "password123",
            "password_confirm": "password123",
        },
        follow_redirects=True,
    )
