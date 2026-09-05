from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token, UserUpdate
from app.core.security import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        full_name=user_in.full_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/token", response_model=Token)
def login(form_data: dict, db: Session = Depends(get_db)):
    # Accept both OAuth2 form or simple JSON {"username":"...","password":"..."}
    username = form_data.get("username") or form_data.get("email")
    password = form_data.get("password")
    if not username or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing credentials")
    user = db.query(User).filter(User.email == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
def update_me(update: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if update.full_name is not None:
        current_user.full_name = update.full_name
    if update.password:
        current_user.password_hash = get_password_hash(update.password)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/logout")
def logout():
    # For JWT stateless tokens logout is client-side; provide endpoint for symmetry
    return {"msg": "logged out"}
