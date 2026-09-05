from sqlalchemy.orm import Session
from app.db.session import init_engine, get_session
from app.models.user import User
from app.models.golfer_profile import GolferProfile
from app.models.club import Club
from app.models.course import Course
from app.models.hole import Hole
from app.core.security import get_password_hash


def seed(engine_url: str = None):
    init_engine(engine_url)
    db: Session = get_session()

    try:
        # create sample user if not exists
        user = db.query(User).filter(User.email == 'sample@golfer.local').first()
        if not user:
            user = User(email='sample@golfer.local', password_hash=get_password_hash('password'), full_name='Sample Golfer')
            db.add(user)
            db.commit()
            db.refresh(user)

        # create golfer profile
        profile = db.query(GolferProfile).filter(GolferProfile.user_id == user.id).first()
        if not profile:
            profile = GolferProfile(user_id=user.id, handicap=12.5, preferred_tee='White')
            db.add(profile)
            db.commit()

        # clubs
        existing = db.query(Club).filter(Club.user_id == user.id).all()
        if not existing:
            clubs = [
                ('Driver', 245),
                ('3 Wood', 220),
                ('5 Iron', 185),
                ('7 Iron', 165),
                ('9 Iron', 140),
                ('Pitching Wedge', 125),
                ('Putter', 20)
            ]
            for name, dist in clubs:
                db.add(Club(user_id=user.id, name=name, total_distance=dist, carry_distance=dist * 0.9))
            db.commit()

        # sample course + holes
        course = db.query(Course).filter(Course.name == 'Sample Golf Club').first()
        if not course:
            course = Course(name='Sample Golf Club', city='Hometown', state='CA')
            db.add(course)
            db.commit()
            db.refresh(course)
            # create 18 holes
            for i in range(1, 19):
                db.add(Hole(course_id=course.id, hole_number=i, par=4 if i % 3 != 0 else 3, yardage=350 - (i * 5)))
            db.commit()

        print('Seed completed')
    finally:
        db.close()


if __name__ == '__main__':
    seed()
