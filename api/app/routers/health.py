"""Liveness check.

The start scripts poll this until it answers, which is how they know the stack is up and it's
safe to open the browser. Keep it cheap and keep it dependency-free.
"""

from fastapi import APIRouter

from ..db import backend_name
from ..models import Health

router = APIRouter(tags=["health"])

VERSION = "0.2.0"


@router.get("/health", response_model=Health)
@router.get("/api/health", response_model=Health)
def health():
    """Served on both paths on purpose.

    `/health` is what the start scripts hit directly on port 8000. `/api/health` is what the
    browser can reach, because both nginx and the Vite dev server only forward `/api/`.
    """
    return Health(status="ok", database=backend_name(), version=VERSION)
