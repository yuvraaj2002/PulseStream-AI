from fastapi import APIRouter, Depends
from utils.jwt_handler import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("/my-tasks")
def get_user_tasks(current_user: dict = Depends(get_current_user)):
    """Example of a protected route."""
    return {
        "message": f"Tasks fetched successfully for {current_user['email']}"
    }
