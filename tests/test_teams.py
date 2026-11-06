import unittest
from fractions import Fraction
from datetime import datetime

import helpers
from helpers import player
import teams
from scoring import PlayerPoints
from loader import Lineup

ROLES = ["WK", "BAT", "BAT", "BAT", "BAT", "AR", "AR", "BOWL", "BOWL", "BOWL", "BOWL"]


def make_pool(credits, team_codes):
    return {f"P{i}": player(f"P{i}", team_codes[i], ROLES[i], credits[i]) for i in range(11)}


EXACT_100 = ["10.0"] + ["9.0"] * 10
SEVEN_AND_FOUR = ["A"] * 7 + ["B"] * 4
IDS = [f"P{i}" for i in range(11)]


class ValidationTests(unittest.TestCase):
    def check(self, pool, captain="P0", vice="P1", ids=IDS):
        return teams.validate_team(ids, captain, vice, pool, ("A", "B"))

    def test_edge_credits_exactly_100_and_seven_from_one_team(self):
        self.assertIsNone(self.check(make_pool(EXACT_100, SEVEN_AND_FOUR)))

    def test_credits_over_100(self):
        pool = make_pool(["10.1"] + ["9.0"] * 10, SEVEN_AND_FOUR)
        self.assertEqual(self.check(pool), "CREDITS_EXCEEDED")

    def test_eight_from_one_team(self):
        pool = make_pool(EXACT_100, ["A"] * 8 + ["B"] * 3)
        self.assertEqual(self.check(pool), "TOO_MANY_FROM_ONE_TEAM")

    def test_captain_and_vice_must_differ_and_be_in_team(self):
        pool = make_pool(EXACT_100, SEVEN_AND_FOUR)
        self.assertEqual(self.check(pool, "P0", "P0"), "CAPTAIN_VICE_INVALID")
        self.assertEqual(self.check(pool, "P0", "P99"), "CAPTAIN_VICE_INVALID")

    def test_team_size_duplicates_unknown_and_other_team(self):
        pool = make_pool(EXACT_100, SEVEN_AND_FOUR)
        self.assertEqual(self.check(pool, ids=IDS[:10]), "TEAM_SIZE_INVALID")
        self.assertEqual(self.check(pool, ids=IDS[:10] + ["P0"]), "DUPLICATE_PLAYER")
        self.assertEqual(self.check(pool, ids=IDS[:10] + ["PX"]), "UNKNOWN_PLAYER")
        pool["P3"] = player("P3", "C", "BAT", "9.0")
        self.assertEqual(self.check(pool), "PLAYER_NOT_IN_MATCH")

    def test_role_limits(self):
        pool = make_pool(EXACT_100, SEVEN_AND_FOUR)
        pool["P1"] = player("P1", "A", "WK", "9.0")   # now 2 WK, 3 BAT -> still valid
        self.assertIsNone(self.check(pool))
        for pid in ("P1", "P2", "P3"):                 # only 1 BAT left -> invalid
            pool[pid] = player(pid, "A", "WK", "9.0")
        self.assertEqual(self.check(pool), "ROLE_LIMIT_VIOLATED")

    def test_lock_time_is_one_minute_before_start(self):
        start = datetime(2026, 10, 17, 19, 30, 0)
        self.assertEqual(teams.lock_time(start), datetime(2026, 10, 17, 19, 29, 0))


def pts(total):
    f = Fraction(total)
    return PlayerPoints("M", "x", 0, 0, 0, 0, f, f * 0, 0, f * 0, f * 0, f * 0, f * 0, f)


class ScoreTests(unittest.TestCase):
    def test_xi_bonus_before_multiplier(self):
        # the +4 is already inside the player's total: (58 + 4) x 2 = 124
        points = {"A": pts(62), "B": pts(10)}
        self.assertEqual(teams.team_score(["A", "B"], "A", "B", points, {}), 124 + 15)

    def test_vice_captain_1_5(self):
        points = {"A": pts(10), "B": pts(10)}
        self.assertEqual(teams.team_score(["A", "B"], "A", "B", points, {}), Fraction(35))

    def test_edge_substitute_not_in_team_gets_half(self):
        points = {"OLD": pts(0), "SUB": pts(12), "Z": pts(10)}
        subs = {"OLD": "SUB"}
        self.assertEqual(teams.team_score(["OLD", "Z"], "Z", "OLD", points, subs),
                         Fraction(20) + Fraction(3, 2) * Fraction(6))

    def test_edge_substitute_already_in_team_gives_zero_for_listed_player(self):
        points = {"OLD": pts(0), "SUB": pts(12), "Z": pts(10)}
        subs = {"OLD": "SUB"}
        self.assertEqual(teams.team_score(["OLD", "SUB"], "Z", "SUB", points, subs),
                         Fraction(12) * Fraction(3, 2))

    def test_substitute_map(self):
        rows = [Lineup("M", "A", "P1", True, ""), Lineup("M", "A", "P2", True, "P1")]
        self.assertEqual(teams.substitute_map(rows), {"P1": "P2"})


if __name__ == "__main__":
    unittest.main()
