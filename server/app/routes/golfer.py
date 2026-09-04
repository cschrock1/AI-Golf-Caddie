from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.golfer_profile import GolferProfile
from app.models.user import User
from app.schemas.golfer import (
    GolferProfileCreate,
    GolferProfileResponse,
)

router = APIRouter(prefix="/golfer", tags=["Golfer"])


@router.get(
    "/{user_id}",
    response_model=GolferProfileResponse
)
def get_golfer_profile(
    user_id: int,
    db: Session = Depends(get_db)
):
    profile = db.query(GolferProfile).filter(
        GolferProfile.user_id == user_id
    ).first()
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Golfer profile not found")
    return profile


@router.post(
    "/",
    response_model=GolferProfileResponse,
    status_code=status.HTTP_201_CREATED
)
def create_golfer_profile(
    profile: GolferProfileCreate,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == profile.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db_profile = GolferProfile(
        user_id=profile.user_id,
        handicap=profile.handicap,
        preferred_tee=profile.preferred_tee
    )

    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)

    return db_profile


@router.put(
    "/{user_id}",
    response_model=GolferProfileResponse
)
def update_golfer_profile(
    user_id: int,
    profile: GolferProfileCreate,
    db: Session = Depends(get_db)
):
    db_profile = db.query(GolferProfile).filter(GolferProfile.user_id == user_id).first()
    if not db_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Golfer profile not found")
    if db_profile.user_id != profile.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User mismatch")

    db_profile.handicap = profile.handicap
    db_profile.preferred_tee = profile.preferred_tee

    db.commit()
    db.refresh(db_profile)
    return db_profile
