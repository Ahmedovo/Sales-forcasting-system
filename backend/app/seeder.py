from __future__ import annotations
from . import create_app
from .extensions import db
from .models import User


def ensure_admin_user(username: str = 'admin', email: str = 'admin@example.com', password: str = 'password') -> None:
    user = User.query.filter((User.username == username) | (User.email == email)).first()
    if user:
        return
    db.session.add(User(username=username, email=email, password_hash=password))
    db.session.commit()


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        ensure_admin_user()
        print('Admin user ensured')


