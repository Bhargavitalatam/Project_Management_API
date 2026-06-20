from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import settings

db_url = settings.DATABASE_URL
# Handle standard Heroku-style or older connection strings if they start with postgres://
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
