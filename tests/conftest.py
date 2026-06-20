import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import get_db
from src.models.base import Base
from src.main import app
from fastapi.testclient import TestClient

# SQLite database URL for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_api.db"

# Create engine and sessionmaker for isolated test database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    # Set up tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clean up tables
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    # Override get_db to return our isolated test database session
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
