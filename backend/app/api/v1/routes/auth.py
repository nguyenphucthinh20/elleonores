from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserCreate, UserLogin, TokenSchema
from app.db.neo4j import Neo4jDB, get_db
from app.core.security import (
    authenticate_user,
    create_access_token,
    hash_password,
)

router = APIRouter(prefix="/auth", tags=["Login"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def register(
    user: UserCreate,
    db: Neo4jDB = Depends(get_db)
    ):
    existing_user = await db.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists. Please use a different email."
        )
    hashed_password = hash_password(user.password)
    await db.create_user(user.email, hashed_password, user.username)
    return {"message": "User registered successfully"}

@router.post("/login", response_model=TokenSchema)
async def login(
    user: OAuth2PasswordRequestForm = Depends(),
    db: Neo4jDB = Depends(get_db)
    ):
    auth_user = await authenticate_user(db, user.username, user.password)
    if not auth_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token(auth_user["username"])
    return {"access_token": token}
