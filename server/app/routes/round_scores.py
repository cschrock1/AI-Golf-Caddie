from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.round import Round
from app.models.hole import Hole
from app.models.round_score import RoundScore
from app.schemas.round_score import RoundScoreCreate, RoundScoreResponse
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter(prefix="/round_scores", tags=["RoundScores"])


def serialize_score(score: RoundScore) -> dict:
    return {
        "id": score.id,
        "round_id": score.round_id,
        "hole_id": score.hole_id,
        "hole_number": score.hole.hole_number,
        "strokes": score.strokes,
    }


@router.get("/", response_model=list[RoundScoreResponse])
def get_round_scores(
    round_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_round = db.query(Round).filter(Round.id == round_id).first()
    if not db_round:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Round not found")
    if db_round.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view these scores")
    scores = db.query(RoundScore).filter(RoundScore.round_id == round_id).all()
    return [serialize_score(score) for score in scores]


@router.post("/batch", response_model=list[RoundScoreResponse], status_code=status.HTTP_200_OK)
def upsert_round_scores(
    user_id: int,
    round_id: int,
    scores: list[RoundScoreCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this round")
    db_round = db.query(Round).filter(Round.id == round_id).first()
    if not db_round:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Round not found")
    if db_round.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this round")

    resolved_scores: dict[int, int] = {}
    for score in scores:
        hole = None
        if score.hole_id:
            hole = db.query(Hole).filter(Hole.id == score.hole_id, Hole.course_id == db_round.course_id).first()
        elif getattr(score, 'hole_number', None) is not None:
            # find hole by course and hole_number
            hole = db.query(Hole).filter(
                Hole.course_id == db_round.course_id,
                Hole.hole_number == score.hole_number
            ).first()

        if not hole:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Hole not found for input {score.hole_id or score.hole_number}")

        # If a batch repeats a hole, the last supplied score wins.
        resolved_scores[hole.id] = score.strokes

    results: list[RoundScore] = []
    for hole_id, strokes in resolved_scores.items():
        statement = (
            insert(RoundScore)
            .values(round_id=round_id, hole_id=hole_id, strokes=strokes)
            .on_conflict_do_update(
                index_elements=[RoundScore.round_id, RoundScore.hole_id],
                set_={"strokes": strokes},
            )
            .returning(RoundScore)
        )
        results.append(db.execute(statement).scalar_one())

    db.commit()

    return [serialize_score(score) for score in results]
