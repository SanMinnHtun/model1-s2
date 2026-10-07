"""FastAPI application entry point."""

from fastapi import FastAPI

from routes.quiz import router as quiz_router

app = FastAPI()
app.include_router(quiz_router)


@app.get("/")
def root() -> dict[str, str]:
    """Basic health check."""
    return {"status": "ok"}
