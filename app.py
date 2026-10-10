"""FastAPI application entry point."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.quiz import router as quiz_router

app = FastAPI()

# Set FRONTEND_URL on Render to the deployed Vercel origin, for example
# https://my-career-quiz.vercel.app. Multiple origins can be comma-separated.
frontend_origins = [
    origin.strip().rstrip("/")
    for origin in os.getenv("FRONTEND_URL", "http://localhost:3000").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

app.include_router(quiz_router)


@app.get("/")
def root() -> dict[str, str]:
    """Basic health check."""
    return {"status": "ok"}
