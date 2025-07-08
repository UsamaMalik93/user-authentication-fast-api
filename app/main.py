# Import FastAPI framework
from fastapi import FastAPI
# Import the authentication router
from app.api.routes import auth

# Create the FastAPI application instance
app = FastAPI()

# Include the authentication router under the /auth prefix
app.include_router(auth.router, prefix="/auth", tags=["auth"]) 