from enum import StrEnum
from fastapi import HTTPException
from app.modules.users.models import User

class UserRole(StrEnum):
    ADMIN = "admin"
    DIRECTOR = "director"
    SUPERVISOR = "supervisor"



def check_branch_access(current_user, branch_id):
    if current_user.role == "admin":
        return True

    if current_user.branch_id != branch_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied for this branch",
        )

    return True