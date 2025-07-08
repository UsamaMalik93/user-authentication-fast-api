from app.db.session import SessionLocal
from fastapi import Depends

# Dependency to provide a database session to FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 