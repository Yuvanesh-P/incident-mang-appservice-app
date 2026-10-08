from fastapi import FastAPI
from sqlalchemy import text

from .database import Base, engine
from . import models
from .routers import auth, incidents


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Incident Management API",
    description=(
        "Backend API for managing operational incidents, "
        "authentication, severity and incident lifecycle."
    ),
    version="1.0.0"
)


app.include_router(auth.router)
app.include_router(incidents.router)


@app.get("/")
def root():
    return {
        "application": "Incident Management API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "incident-management-api"
    }


@app.get("/db-health")
def database_health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "database": "connected"
        }

    except Exception as error:
        return {
            "database": "connection failed",
            "error": str(error)
        }