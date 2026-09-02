from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo.errors import PyMongoError
from datetime import datetime

from app.mongodb import users_collection

from app.models.auth_model import (
    UserRegister,
    UserLogin,
    Token,
    UserResponse
)

from app.auth_utils import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

security = HTTPBearer()


# =========================================================
# REGISTER
# =========================================================

@router.post(
    "/register",
    response_model=UserResponse
)
def register_user(
    user: UserRegister
):

    try:

        existing_username = users_collection.find_one(
            {
                "username": user.username
            }
        )

        if existing_username:

            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )


        existing_email = users_collection.find_one(
            {
                "email": user.email
            }
        )

        if existing_email:

            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )


        # Hash password before storing it
        hashed_password = hash_password(
            user.password
        )


        # Store user in MongoDB
        users_collection.insert_one({

            "username": user.username,

            "email": user.email,

            "password_hash":
                hashed_password,

            "created_at":
                datetime.utcnow()
        })


        return {

            "username":
                user.username,

            "email":
                user.email
        }


    except HTTPException:

        raise


    except PyMongoError as e:

        raise HTTPException(
            status_code=500,
            detail=f"Database Error: {str(e)}"
        )


# =========================================================
# LOGIN
# =========================================================

@router.post(
    "/login",
    response_model=Token
)
def login_user(
    user: UserLogin
):

    try:

        db_user = users_collection.find_one(
            {
                "username": user.username
            }
        )


        if not db_user:

            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )


        password_valid = verify_password(

            user.password,

            db_user["password_hash"]
        )


        if not password_valid:

            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )


        access_token = create_access_token(
            user.username
        )


        return {

            "access_token":
                access_token,

            "token_type":
                "bearer"
        }


    except HTTPException:

        raise


    except PyMongoError as e:

        raise HTTPException(
            status_code=500,
            detail=f"Database Error: {str(e)}"
        )


# =========================================================
# GET CURRENT USER
# =========================================================

def get_current_user(
    credentials:
        HTTPAuthorizationCredentials =
        Depends(security)
):

    token = credentials.credentials


    payload = decode_access_token(
        token
    )


    if not payload:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


    username = payload.get(
        "sub"
    )


    if not username:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


    user = users_collection.find_one(

        {
            "username":
                username
        },

        {
            "_id": 0,

            "username": 1,

            "email": 1
        }
    )


    if not user:

        raise HTTPException(
            status_code=401,
            detail="User not found"
        )


    return user


# =========================================================
# CURRENT USER
# =========================================================

@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user=Depends(
        get_current_user
    )
):

    return current_user