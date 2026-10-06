from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.course import Course
from app.models.round import Round
from app.models.round_score import RoundScore
from app.models.user import User
from app.schemas.round import RoundCreate, RoundResponse
from app.core.security import get_current_user

router = APIRouter(prefix="/rounds", tags=["Rounds"])


@router.get("/", response_model=list[RoundResponse])
def get_rounds(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view these rounds")
    return db.query(Round).filter(
        Round.user_id == user_id
    ).all()


@router.post("/", response_model=RoundResponse, status_code=status.HTTP_201_CREATED)
def create_round(
    round_data: RoundCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != round_data.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create a round for this user")

    course = db.query(Course).filter(Course.id == round_data.course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    db_round = Round(
        user_id=round_data.user_id,
        course_id=round_data.course_id,
        date=round_data.date,
        score=round_data.score
    )

    db.add(db_round)
    db.commit()
    db.refresh(db_round)

    return db_round


@router.put("/{round_id}", response_model=RoundResponse)
def update_round(
    round_id: int,
    round_data: RoundCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_round = db.query(Round).filter(Round.id == round_id).first()
    if not db_round:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Round not found")
    if db_round.user_id != current_user.id or round_data.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this round")

    db_round.user_id = round_data.user_id
    db_round.course_id = round_data.course_id
    db_round.date = round_data.date
    db_round.score = round_data.score

    db.commit()
    db.refresh(db_round)
    return db_round


@router.delete("/{round_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_round(
    round_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_round = db.query(Round).filter(Round.id == round_id).first()
    if not db_round:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Round not found")
    if db_round.user_id != user_id or current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this round")

    db.delete(db_round)
    db.commit()
    return None


@router.post("/{round_id}/complete", response_model=RoundResponse)
def complete_round(
    round_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_round = db.query(Round).filter(Round.id == round_id).first()
    if not db_round:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Round not found")
    if db_round.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to complete this round")

    scores = db.query(RoundScore).filter(RoundScore.round_id == round_id).all()
    db_round.score = sum(score.strokes for score in scores) or None
    db_round.is_complete = True
    db.commit()
    db.refresh(db_round)
    return db_round
