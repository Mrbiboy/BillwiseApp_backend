import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Your test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def test_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    # Drop tables
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    from main import app

    def override_get_db():
        return test_db

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
