from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.club import Club
from app.models.user import User
from app.schemas.club import ClubCreate, ClubResponse
from app.core.security import get_current_user

router = APIRouter(prefix="/clubs", tags=["Clubs"])


@router.get("/", response_model=list[ClubResponse])
def get_clubs(
    user_id: int,
    db: Session = Depends(get_db)
):
    return db.query(Club).filter(
        Club.user_id == user_id
    ).all()


@router.post("/", response_model=ClubResponse, status_code=status.HTTP_201_CREATED)
def create_club(
    club: ClubCreate,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add club for this user")

    db_club = Club(
        user_id=user_id,
        name=club.name,
        carry_distance=club.carry_distance,
        total_distance=club.total_distance
    )

    db.add(db_club)
    db.commit()
    db.refresh(db_club)

    return db_club


@router.put("/{club_id}", response_model=ClubResponse)
def update_club(
    club_id: int,
    club: ClubCreate,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_club = db.query(Club).filter(Club.id == club_id).first()
    if not db_club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Club not found")
    if db_club.user_id != user_id or current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this club")

    db_club.name = club.name
    db_club.carry_distance = club.carry_distance
    db_club.total_distance = club.total_distance

    db.commit()
    db.refresh(db_club)
    return db_club


@router.delete("/{club_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_club(
    club_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_club = db.query(Club).filter(Club.id == club_id).first()
    if not db_club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Club not found")
    if db_club.user_id != user_id or current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this club")

    db.delete(db_club)
    db.commit()
    return None
