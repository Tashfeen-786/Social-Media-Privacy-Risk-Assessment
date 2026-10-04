"""
app.py
------
FastAPI application entry point for the
Social Media Privacy Risk Assessment Framework.

Run:
    python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
or:
    python backend/app.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv                                  # noqa: E402
from fastapi import FastAPI, Request                            # noqa: E402
from fastapi.middleware.cors import CORSMiddleware              # noqa: E402
from fastapi.responses import JSONResponse                      # noqa: E402
from fastapi.staticfiles import StaticFiles                     # noqa: E402

from backend.routes.api import router as api_router             # noqa: E402
from backend.utils.security import SECURITY_HEADERS, rate_limit_check  # noqa: E402

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = FastAPI(
    title="Social Media Privacy Risk Assessment Framework",
    description=("Privacy-focused cybersecurity framework for assessing social-media "
                 "exposure, account-security practices, social-engineering risk, "
                 "digital-footprint risk and personalised privacy improvements using "
                 "synthetic / self-reported data. Implements two complementary "
                 "educational models: the 10-category PRIVACY ASSESSMENT SCORE and the "
                 "8-category PRIVACY EXPOSURE RUBRIC. Defensive and educational only."),
    version="2.0.0",
)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_and_rate_limit(request: Request, call_next):
    """Adds security headers and applies a simple per-client rate limit."""
    if request.url.path.startswith("/api") and request.method != "OPTIONS":
        client = request.client.host if request.client else "unknown"
        if not rate_limit_check(client):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please retry shortly."},
                headers=SECURITY_HEADERS,
            )
    response = await call_next(request)
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response


app.include_router(api_router)

# Serve the static frontend (index.html, assessment.html, dashboard.html, ...)
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app:app",
                host=os.getenv("HOST", "0.0.0.0"),
                port=int(os.getenv("PORT", "8000")),
                reload=False)
