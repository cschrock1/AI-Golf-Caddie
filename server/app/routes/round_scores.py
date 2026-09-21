from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.round import Round
from app.models.hole import Hole
from app.models.round_score import RoundScore
from app.schemas.round_score import RoundScoreCreate, RoundScoreResponse

router = APIRouter(prefix="/round_scores", tags=["RoundScores"])


@router.get("/", response_model=list[RoundScoreResponse])
def get_round_scores(
    round_id: int,
    db: Session = Depends(get_db)
):
    return db.query(RoundScore).filter(RoundScore.round_id == round_id).all()


@router.post("/batch", response_model=list[RoundScoreResponse], status_code=status.HTTP_200_OK)
def upsert_round_scores(
    user_id: int,
    round_id: int,
    scores: list[RoundScoreCreate],
    db: Session = Depends(get_db)
):
    db_round = db.query(Round).filter(Round.id == round_id).first()
    if not db_round:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Round not found")
    if db_round.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this round")

    results: list[RoundScore] = []
    for score in scores:
        hole = None
        if score.hole_id:
            hole = db.query(Hole).filter(Hole.id == score.hole_id).first()
        elif getattr(score, 'hole_number', None) is not None:
            # find hole by course and hole_number
            hole = db.query(Hole).filter(
                Hole.course_id == db_round.course_id,
                Hole.hole_number == score.hole_number
            ).first()

        if not hole:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Hole not found for input {score.hole_id or score.hole_number}")

        db_score = db.query(RoundScore).filter(
            RoundScore.round_id == round_id,
            RoundScore.hole_id == hole.id
        ).first()

        if db_score:
            db_score.strokes = score.strokes
        else:
            db_score = RoundScore(round_id=round_id, hole_id=hole.id, strokes=score.strokes)
            db.add(db_score)

        results.append(db_score)

    db.commit()

    # refresh objects
    for r in results:
        db.refresh(r)

    return results
