import unittest
from types import SimpleNamespace

from app.services.recommendation import choose_clubs, distance_yards


class RecommendationServiceTests(unittest.TestCase):
    def test_distance_yards_uses_longitude_latitude_order(self):
        distance = distance_yards((-86.0, 41.0), (-86.0, 41.001))
        self.assertGreater(distance, 100)
        self.assertLess(distance, 130)

    def test_chooses_shortest_club_that_covers_target_and_returns_alternative(self):
        clubs = [
            SimpleNamespace(id=1, name="7 iron", carry_distance=145, total_distance=155),
            SimpleNamespace(id=2, name="8 iron", carry_distance=132, total_distance=140),
            SimpleNamespace(id=3, name="9 iron", carry_distance=120, total_distance=128),
        ]

        primary, alternative = choose_clubs(clubs, 125)

        self.assertEqual(primary[0].name, "8 iron")
        self.assertEqual(alternative[0].name, "9 iron")

    def test_uses_longest_available_club_when_none_reaches_target(self):
        clubs = [
            SimpleNamespace(id=1, name="5 iron", carry_distance=170, total_distance=180),
            SimpleNamespace(id=2, name="7 iron", carry_distance=145, total_distance=155),
        ]

        primary, _ = choose_clubs(clubs, 205)

        self.assertEqual(primary[0].name, "5 iron")

    def test_ignores_clubs_without_a_positive_distance(self):
        clubs = [
            SimpleNamespace(id=1, name="Putter", carry_distance=None, total_distance=0),
        ]

        self.assertEqual(choose_clubs(clubs, 25), (None, None))


if __name__ == "__main__":
    unittest.main()
