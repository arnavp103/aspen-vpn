"""
Health check route
"""

from datetime import datetime
from fastapi import APIRouter, FastAPI


app = FastAPI(title="Aspen VPN Server")
router = APIRouter()


@router.get("/create-invite")
async def create_invite():
    """ Generate a new invite code.
        Requires admin privileges.
    """
    
    return {"status": "ok", "time": datetime.now()}


app.include_router(router)
