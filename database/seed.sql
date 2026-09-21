-- Development-only seed data for local testing.
-- This is not for production use.

INSERT INTO users (id, email, password_hash)
VALUES (1, 'test@example.com', 'development-only')
ON CONFLICT (id) DO NOTHING;

INSERT INTO golfer_profiles (id, user_id, handicap, preferred_tee)
VALUES (1, 1, 8.5, 'Blue')
ON CONFLICT (id) DO NOTHING;

INSERT INTO clubs (id, user_id, name, carry_distance, total_distance)
VALUES
    (1, 1, 'Driver', 265, 280),
    (2, 1, '5 Iron', 205, 215),
    (3, 1, '7 Iron', 175, 185),
    (4, 1, '9 Iron', 145, 155),
    (5, 1, 'Pitching Wedge', 125, 135)
ON CONFLICT (id) DO NOTHING;

INSERT INTO courses (id, name, city, state)
VALUES (1, 'Test Golf Course', 'Goshen', 'Indiana')
ON CONFLICT (id) DO NOTHING;

INSERT INTO holes (id, course_id, hole_number, par, yardage)
VALUES
    (1, 1, 1, 4, 385),
    (2, 1, 2, 5, 475),
    (3, 1, 3, 3, 165),
    (4, 1, 4, 4, 385),
    (5, 1, 5, 4, 410),
    (6, 1, 6, 3, 175),
    (7, 1, 7, 3, 190),
    (8, 1, 8, 5, 510),
    (9, 1, 9, 4, 400),
    (10, 1, 10, 4, 395),
    (11, 1, 11, 5, 500),
    (12, 1, 12, 4, 410),
    (13, 1, 13, 3, 180),
    (14, 1, 14, 4, 420),
    (15, 1, 15, 5, 515),
    (16, 1, 16, 4, 405),
    (17, 1, 17, 3, 170),
    (18, 1, 18, 4, 390)
ON CONFLICT (id) DO NOTHING;

INSERT INTO rounds (id, user_id, course_id, date, score)
VALUES (1, 1, 1, '2026-09-03', 82)
ON CONFLICT (id) DO NOTHING;

INSERT INTO shots (id, round_id, hole_id, club_id, start_distance, end_distance, result)
VALUES
    (1, 1, 1, 1, 385, 120, 'Fairway'),
    (2, 1, 1, 5, 120, 8, 'Green')
ON CONFLICT (id) DO NOTHING;
