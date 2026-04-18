import shutil
from datetime import date
from pathlib import Path
from uuid import uuid4

import pytest

from app import create_app
from app.extensions import db


TEST_RUNTIME_DIR = Path(__file__).resolve().parent / ".runtime"
TEST_RUNTIME_DIR.mkdir(exist_ok=True)


@pytest.fixture()
def app():
    case_dir = TEST_RUNTIME_DIR / f"case_{uuid4().hex}"
    case_dir.mkdir(parents=True, exist_ok=True)
    db_path = case_dir / "test.db"

    class TestConfig:
        TESTING = True
        SECRET_KEY = "test-secret"
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
        SQLALCHEMY_TRACK_MODIFICATIONS = False

    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
    shutil.rmtree(case_dir, ignore_errors=True)


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def current_period():
    today = date.today()
    return today.month, today.year
