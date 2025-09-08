from fastapi import APIRouter, HTTPException
from storage.memory import storage
from schemas.user import UserRegister, UserLogin, UserPublic
from core.logging import logger

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserPublic)
async def register_user(payload: UserRegister):
    try:
        logger.info(f"API users.register: email={payload.email}")
        user = storage.create_user(email=payload.email, full_name=payload.full_name, password=payload.password)
        logger.info(f"API users.register.ok: email={payload.email}")
        return UserPublic(email=user["email"], full_name=user["full_name"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail="Failed to register user")


@router.post("/login", response_model=UserPublic)
async def login_user(payload: UserLogin):
    try:
        logger.info(f"API users.login: email={payload.email}")
        user = storage.authenticate_user(payload.email, payload.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        logger.info(f"API users.login.ok: email={payload.email}")
        return UserPublic(email=user["email"], full_name=user["full_name"]) 
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in user: {e}")
        raise HTTPException(status_code=500, detail="Failed to login user")
