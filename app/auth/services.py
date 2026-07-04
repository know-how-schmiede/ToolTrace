from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import or_

from app.extensions import db
from app.models import User


class AuthService:
    def register_user(
        self,
        *,
        email: str,
        username: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        existing = User.query.filter(or_(User.email == email.lower(), User.username == username)).first()
        if existing:
            raise ValueError("E-Mail oder Benutzername ist bereits vergeben.")

        user = User(
            email=email.lower(),
            username=username,
            first_name=first_name or None,
            last_name=last_name or None,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    def record_login(self, user: User) -> None:
        user.last_login_at = datetime.now(timezone.utc)
        db.session.commit()
