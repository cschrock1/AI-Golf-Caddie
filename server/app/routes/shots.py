from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.club import Club
from app.models.hole import Hole
from app.models.round import Round
from app.models.shot import Shot
from app.schemas.shot import ShotCreate, ShotResponse

router = APIRouter(prefix="/shots", tags=["Shots"])


@router.get("/", response_model=list[ShotResponse])
def get_shots(
    round_id: int,
    db: Session = Depends(get_db)
):
    return db.query(Shot).filter(
        Shot.round_id == round_id
    ).all()


@router.post("/", response_model=ShotResponse, status_code=status.HTTP_201_CREATED)
def create_shot(
    shot: ShotCreate,
    db: Session = Depends(get_db)
):
    round = db.query(Round).filter(Round.id == shot.round_id).first()
    if not round:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Round not found")

    hole = db.query(Hole).filter(Hole.id == shot.hole_id).first()
    if not hole:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hole not found")

    club = db.query(Club).filter(Club.id == shot.club_id).first()
    if not club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Club not found")

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
    db: Session = Depends(get_db)
):
    db_shot = db.query(Shot).filter(Shot.id == shot_id).first()
    if not db_shot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shot not found")

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
    db: Session = Depends(get_db)
):
    db_shot = db.query(Shot).filter(Shot.id == shot_id).first()
    if not db_shot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shot not found")

    db.delete(db_shot)
    db.commit()
    return None
