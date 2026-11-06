import unittest
from fractions import Fraction

import helpers
from helpers import ball
import scoring as sc


class BandTests(unittest.TestCase):
    def test_milestone_highest_only(self):
        self.assertEqual([sc.milestone_bonus(r) for r in (29, 30, 49, 50, 99, 100)],
                         [0, 4, 4, 8, 8, 16])

    def test_strike_rate_edges(self):
        # balls = 100, so runs = strike rate
        # above 170 +6; 150-170 +4; 130-<150 +2; 70-130 0; 60-70 -2; 50-<60 -4; <50 -6
        cases = {171: 6, 170: 4, 150: 4, 149: 2, 130: 2, 129: 0, 71: 0,
                 70: -2, 60: -2, 59: -4, 50: -4, 49: -6}
        for runs, expected in cases.items():
            self.assertEqual(sc.strike_rate_points(runs, 100), expected, runs)

    def test_strike_rate_needs_10_balls(self):
        self.assertEqual(sc.strike_rate_points(30, 9), 0)

    def test_strike_rate_exact_fraction(self):
        # 17 off 10 is exactly 170 -> not above 170 -> +4
        self.assertEqual(sc.strike_rate_points(17, 10), 4)

    def test_economy_edges(self):
        # runs conceded in 24 balls (4 overs): economy = runs / 4
        cases = {19: 6, 20: 4, 24: 4, 25: 2, 28: 2, 29: 0, 39: 0, 40: -2,
                 44: -2, 45: -4, 48: -4, 49: -6}
        for runs, expected in cases.items():
            self.assertEqual(sc.economy_points(runs, 24), expected, runs)

    def test_economy_needs_2_overs(self):
        self.assertEqual(sc.economy_points(0, 11), 0)
        self.assertEqual(sc.economy_points(0, 12), 6)

    def test_haul_highest_only(self):
        self.assertEqual([sc.haul_bonus(w) for w in (2, 3, 4, 5, 6)], [0, 4, 8, 16, 16])


class EventTests(unittest.TestCase):
    def test_edge_30_runs_off_10_balls(self):
        # 4 fours, 2 sixes, 2 singles... = 30 runs in 10 balls, caught on the 10th
        runs = [4, 4, 4, 4, 6, 6, 1, 1, 0, 0]
        balls = [ball("BAT1", runs=r, seq=i + 1, over=i // 6) for i, r in enumerate(runs)]
        balls[-1] = ball("BAT1", runs=0, seq=10, over=1, wicket="CAUGHT",
                         out="BAT1", f1="FLD")
        stats = sc.collect_stats(balls)["BAT1"]
        self.assertEqual((stats.runs, stats.balls, stats.fours, stats.sixes), (30, 10, 4, 2))
        bat, sr = sc.batting_points(stats, "BAT")
        # 30 runs + 4 (fours) + 4 (sixes) + 4 (30 bonus) = 42, SR 300 gives +6
        self.assertEqual((bat, sr), (42, 6))

    def test_edge_two_overs_economy_exactly_5(self):
        # 12 legal balls, 10 runs -> economy exactly 5.0 -> +4
        balls = [ball(runs=1, seq=i + 1, over=i // 6, bowler="BW") for i in range(10)]
        balls += [ball(runs=0, seq=11, over=1, bowler="BW"),
                  ball(runs=0, seq=12, over=1, bowler="BW")]
        stats = sc.collect_stats(balls)["BW"]
        self.assertEqual((stats.legal_balls, stats.runs_conceded), (12, 10))
        self.assertEqual(sc.bowling_points(stats)[1], 4)

    def test_edge_run_out_shared_by_two_fielders(self):
        balls = [ball("A", runs=0, wicket="RUN_OUT", out="A", f1="F1", f2="F2", direct=False)]
        stats = sc.collect_stats(balls)
        self.assertEqual(sc.fielding_points(stats["F1"]), 3)
        self.assertEqual(sc.fielding_points(stats["F2"]), 3)

    def test_direct_run_out_and_run_out_gives_bowler_nothing(self):
        balls = [ball("A", wicket="RUN_OUT", out="A", f1="F1", direct=True)]
        stats = sc.collect_stats(balls)
        self.assertEqual(sc.fielding_points(stats["F1"]), 12)
        self.assertEqual(stats["B"].wickets, 0)

    def test_wides_and_no_balls(self):
        balls = [ball("A", runs=0, extras="WIDE", extras_runs=1),
                 ball("A", runs=2, extras="NOBALL", extras_runs=1, seq=2),
                 ball("A", runs=0, extras="BYE", extras_runs=1, seq=3)]
        stats = sc.collect_stats(balls)
        self.assertEqual(stats["A"].balls, 2)            # wide is not a ball faced
        self.assertEqual(stats["B"].legal_balls, 1)      # only the bye is legal
        self.assertEqual(stats["B"].runs_conceded, 1 + 3)  # wide 1, no-ball 1 + 2 off bat

    def test_maiden_over(self):
        balls = [ball(bowler="M", seq=i + 1) for i in range(6)]
        balls += [ball(bowler="N", runs=1 if i == 0 else 0, seq=i + 1, over=1) for i in range(6)]
        stats = sc.collect_stats(balls)
        self.assertEqual(stats["M"].maidens, 1)
        self.assertEqual(stats["N"].maidens, 0)

    def test_wicket_bonuses(self):
        balls = [ball("A", wicket="LBW", out="A", seq=1),
                 ball("B", wicket="BOWLED", out="B", seq=2),
                 ball("C", wicket="CAUGHT", out="C", f1="F", seq=3)]
        stats = sc.collect_stats(balls)["B"]
        self.assertEqual(stats.wickets, 3)
        self.assertEqual(sc.bowling_points(stats)[0], 75 + 16 + 4)   # 3 wickets, 2 LBW/bowled, haul 3

    def test_duck_rules(self):
        out_for_zero = sc.Stats(runs=0, balls=2, out=True)
        self.assertEqual(sc.batting_points(out_for_zero, "BAT")[0], -2)
        self.assertEqual(sc.batting_points(out_for_zero, "BOWL")[0], 0)
        self.assertEqual(sc.batting_points(sc.Stats(runs=0, balls=2, out=False), "BAT")[0], 0)

    def test_three_catches_bonus(self):
        self.assertEqual(sc.fielding_points(sc.Stats(catches=3)), 28)
        self.assertEqual(sc.fielding_points(sc.Stats(catches=2)), 16)

    def test_total_legal_balls(self):
        balls = [ball(seq=1), ball(extras="WIDE", extras_runs=1, seq=2), ball(seq=3)]
        self.assertEqual(sc.total_legal_balls(balls), 2)


if __name__ == "__main__":
    unittest.main()
