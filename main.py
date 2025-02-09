"""FastAPI Application Entry Point.

This module serves as the main entry point for the FastAPI application. It sets up the
application with necessary middleware and routers, and defines the base application
configuration.

Features:
    - CORS Middleware configuration for handling Cross-Origin Resource Sharing
    - Rate limiting implementation using slowapi
    - API routers for different endpoints:
        - /api/utils - Utility endpoints
        - /api/contacts - Contact management endpoints
        - /api/auth - Authentication endpoints
        - /api/users - User management endpoints

Configuration:
    - CORS is enabled for localhost:8000
    - Rate limiting is implemented to prevent abuse
    - Multiple workers (4) for better performance
    - Debug mode enabled with auto-reload
"""

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from src.api import utils, contacts, auth, users
from src.conf import messages
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": "Перевищено ліміт запитів. Спробуйте пізніше."},
    )

app.include_router(utils.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": messages.WELCOME_MESSAGE}


if __name__ == "__main__":

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, workers=4)