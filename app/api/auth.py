import uuid
from datetime import datetime, UTC

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette import status
from starlette.status import HTTP_401_UNAUTHORIZED

from app.core.security import hash_password, verify_password, create_access_token, get_current_user
from app.db.postgres import get_db
from app.models.models import UserCreate, UserRead
from app.models.sql import User

router = APIRouter()

@router.post("/auth/register", tags=["auth"], status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Registers a new user. This function handles the registration of a new user by accepting
    user details and storing them in the database. It ensures that the email is unique and
    that the password meets the required criteria. After successful registration, the function
    returns a success message or the newly created user object.

    :param: email: The email address of the user.
    :type: email: str
    :param: password: The password for the user.
    :type: password: str
    :return: A success message or the newly created user object.
    """

    email = user.email
    password = user.password

    # Check if user already exists
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Hash password
    hashed_password = hash_password(password)

    # Create a new user
    new_user = User(
        id=str(uuid.uuid4()),
        email=email,
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False,
        created_at=datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
    )

    # Add new user to the database
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Create user read model
    user_data = UserRead(
        id=new_user.id,
        email=new_user.email,
        is_active=new_user.is_active,
        is_superuser=new_user.is_superuser,
        created_at=new_user.created_at,
    )

    return {"message": "User registered successfully", "user": user_data}


@router.post("/auth/login", tags=["auth"])
async def login(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Logs in a user. This function handles the login process by validating the user's credentials
    and generating an access token if the credentials are valid. It returns the access token
    and user information if the login is successful. If the credentials are invalid, it raises
    an HTTP exception.

    :param: email: The email address of the user.
    :type: email: str
    :param: password: The password for the user.
    :type: password: str
    :param: db: The database session dependency for interacting with the database.
    :type: db: AsyncSession
    :return: A success message or the access token and user information.

    """
    email = user.email
    password = user.password

    # Validate user credentials
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Generate access token
    access_token = create_access_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user.email,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
        },
    }

@router.get("/users/me", tags=["auth"], response_model=UserRead)
async def read_current_user(current_user: User = Depends(get_current_user)):
    """
    Retrieves the current logged-in user. This function checks the authentication token
    and fetches the user details from the database. It returns the user information if
    the token is valid. If the token is invalid or expired, it raises an HTTP exception.

    :param: token: The authentication token of the user.
    :type: token: str
    :param: db: The database session dependency for interacting with the database.
    :type: db: AsyncSession
    :return: The current user information.
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "is_superuser": current_user.is_superuser,
        "created_at": current_user.created_at,
    }
