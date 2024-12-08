"""
Health check route
"""

from datetime import datetime
from fastapi import APIRouter, FastAPI


app = FastAPI(title="Aspen VPN Server")
router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok", "time": datetime.now()}


app.include_router(router)
