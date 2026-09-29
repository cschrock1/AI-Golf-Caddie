from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.club import Club
from app.models.hole import Hole
from app.models.round import Round
from app.models.shot import Shot
from app.schemas.shot import ShotCreate, ShotResponse
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter(prefix="/shots", tags=["Shots"])


@router.get("/", response_model=list[ShotResponse])
def get_shots(
    round_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_round = db.query(Round).filter(Round.id == round_id).first()
    if not db_round:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Round not found")
    if db_round.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view these shots")
    return db.query(Shot).filter(Shot.round_id == round_id).order_by(Shot.id).all()


def validate_shot_references(shot: ShotCreate, current_user: User, db: Session) -> None:
    db_round = db.query(Round).filter(Round.id == shot.round_id).first()
    if not db_round:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Round not found")
    if db_round.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this round")

    hole = db.query(Hole).filter(Hole.id == shot.hole_id).first()
    if not hole:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hole not found")
    if hole.course_id != db_round.course_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Hole does not belong to this round's course")

    club = db.query(Club).filter(Club.id == shot.club_id, Club.user_id == current_user.id).first()
    if not club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Club not found")


@router.post("/", response_model=ShotResponse, status_code=status.HTTP_201_CREATED)
def create_shot(
    shot: ShotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    validate_shot_references(shot, current_user, db)

    db_shot = Shot(
        round_id=shot.round_id,
        hole_id=shot.hole_id,
        club_id=shot.club_id,
        start_distance=shot.start_distance,
        end_distance=shot.end_distance,
        result=shot.result
    )

    db.add(db_shot)
    db.commit()
    db.refresh(db_shot)

    return db_shot


@router.put("/{shot_id}", response_model=ShotResponse)
def update_shot(
    shot_id: int,
    shot: ShotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_shot = db.query(Shot).filter(Shot.id == shot_id).first()
    if not db_shot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shot not found")

    old_round = db.query(Round).filter(Round.id == db_shot.round_id).first()
    if not old_round or old_round.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this shot")
    validate_shot_references(shot, current_user, db)

    db_shot.round_id = shot.round_id
    db_shot.hole_id = shot.hole_id
    db_shot.club_id = shot.club_id
    db_shot.start_distance = shot.start_distance
    db_shot.end_distance = shot.end_distance
    db_shot.result = shot.result

    db.commit()
    db.refresh(db_shot)
    return db_shot


@router.delete("/{shot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shot(
    shot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_shot = db.query(Shot).filter(Shot.id == shot_id).first()
    if not db_shot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shot not found")
    db_round = db.query(Round).filter(Round.id == db_shot.round_id).first()
    if not db_round or db_round.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this shot")

    db.delete(db_shot)
    db.commit()
    return None
