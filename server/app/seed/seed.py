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
        user = db.query(User).filter(User.email == 'sample@golfer.example').first()
        if not user:
            user = User(email='sample@golfer.example', password_hash=get_password_hash('password'), full_name='Sample Golfer')
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
                ('Driver', 245, 270),
                ('3-Wood', 220, 240),
                ('5-Wood', 205, 220),
                ('4-Iron', 190, 205),
                ('5-Iron', 180, 195),
                ('6-Iron', 170, 185),
                ('7-Iron', 160, 175),
                ('8-Iron', 150, 162),
                ('9-Iron', 140, 150),
                ('Pitching Wedge', 125, 135),
                ('Gap Wedge', 110, 120),
                ('Sand Wedge', 95, 105),
                ('Putter', 20, 25)
            ]
            for name, carry, total in clubs:
                db.add(Club(user_id=user.id, name=name, total_distance=total, carry_distance=carry))
            db.commit()

        # development course + holes
        course = db.query(Course).filter(Course.name == 'Stonehedge Golf Course').first()
        if not course:
            course = Course(name='Stonehedge Golf Course', city='Warsaw', state='IN')
            db.add(course)
            db.commit()
            db.refresh(course)

        hole_specs = {
            1: (4, 390),
            2: (5, 510),
            3: (4, 415),
            4: (3, 175),
            5: (4, 386),
            6: (5, 525),
            7: (4, 432),
            8: (3, 168),
            9: (5, 535),
            10: (4, 397),
            11: (3, 158),
            12: (4, 420),
            13: (5, 548),
            14: (4, 401),
            15: (3, 172),
            16: (4, 448),
            17: (4, 413),
            18: (5, 520),
        }

        for hole_number, (par, yardage) in hole_specs.items():
            hole = db.query(Hole).filter(
                Hole.course_id == course.id,
                Hole.hole_number == hole_number
            ).first()
            if not hole:
                db.add(Hole(
                    course_id=course.id,
                    hole_number=hole_number,
                    par=par,
                    yardage=yardage
                ))
        db.commit()

        print('Seed completed')
    finally:
        db.close()


if __name__ == '__main__':
    seed()
