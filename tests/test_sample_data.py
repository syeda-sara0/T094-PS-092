"""Runs the whole engine on the sample pack in data/ and checks every planted scenario."""
import os
import unittest

import helpers
from engine import Engine

DATA = os.path.join(helpers.ROOT, "data")


@unittest.skipUnless(os.path.exists(os.path.join(DATA, "commands.txt")), "sample data missing")
class SampleDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.e = Engine(DATA)
        cls.e.run(os.path.join(DATA, "commands.txt"))
        cls.validation = {(r[0], r[1]): r for r in cls.e.out_validation}
        cls.points = {(r[0], r[1]): r for r in
                      (__import__("report").player_point_row(p)
                       for rows in cls.e.point_rows.values() for p in rows)}

    def standing(self, contest_id, entry_id):
        for s, user in self.e.settled[contest_id].standings:
            if s.entry_id == entry_id:
                return s, user
        return None, None

    def test_ec01_100_credits_seven_from_one_team_valid(self):
        self.assertEqual(self.validation[("EN-0005", "SUBMIT")][3], "ACCEPTED")

    def test_ec02_30_off_10_balls(self):
        row = self.points[("MT-02", "PL-027")]
        self.assertEqual(row[2:6], [30, 10, 4, 2])
        self.assertEqual(row[6:8], ["42.00", "6.00"])        # 48 batting incl. SR
        self.assertEqual(row[13], "52.00")                    # +4 playing XI

    def test_ec03_economy_exactly_5(self):
        self.assertEqual(self.points[("MT-01", "PL-019")][10], "4.00")

    def test_ec04_shared_run_out_both_fielders_in_team(self):
        self.assertEqual(self.validation[("EN-0006", "SUBMIT")][3], "ACCEPTED")
        self.assertEqual(self.points[("MT-01", "PL-013")][11], "11.00")   # catch 8 + 3
        self.assertEqual(self.points[("MT-01", "PL-014")][11], "3.00")

    def test_ec05_three_way_tie_ranks_2_3_4(self):
        top = [(s.rank, s.entry_id, s.prize) for s, _ in self.e.settled["CT-01"].standings[:5]]
        self.assertEqual(top[0][:2], (1, "EN-0001"))
        self.assertEqual([t[0] for t in top[1:4]], [2, 2, 2])
        self.assertEqual([t[1] for t in top[1:4]], ["EN-0002", "EN-0003", "EN-0004"])
        self.assertEqual(top[4][0], 5)
        pool = 352 * 4900 * 85 // 100
        combined = pool * 15 // 100 + pool * 10 // 100 + int(pool * 3 / 100)
        self.assertEqual(sum(t[2] for t in top[1:4]), combined)

    def test_ec06_guaranteed_one_entry(self):
        s, _ = self.standing("CT-03", "EN-0605")
        self.assertEqual(s.prize, 100000)

    def test_ec07_net_turns_positive_first_time(self):
        payout = [p for p in self.e.settled["CT-01"].payouts if p.user_id == "USR-0008"][0]
        self.assertGreater(payout.cum_net, 0)
        self.assertEqual(payout.taxable_increase, payout.cum_net)     # whole positive net
        self.assertEqual(payout.tds, (payout.cum_net * 30 + 50) // 100)

    def test_ec08_substitute_already_in_team(self):
        with_both, _ = self.standing("CT-02", "EN-0407")
        only_listed, _ = self.standing("CT-02", "EN-0408")
        self.assertIsNotNone(with_both)
        self.assertIsNotNone(only_listed)

    def test_extra_traps(self):
        self.assertEqual(self.validation[("EN-0405", "SUBMIT")][3:], ["REJECTED", "MAX_TEAMS_PER_USER"])
        self.assertEqual(self.validation[("EN-0406", "SUBMIT")][3:], ["REJECTED", "CREDITS_EXCEEDED"])
        self.assertEqual(self.validation[("EN-0002", "EDIT")][3:], ["REJECTED", "ENTRY_LOCKED"])
        self.assertEqual(self.validation[("EN-0007", "EDIT")][3], "ACCEPTED")

    def test_rain_shortened_match_is_not_abandoned(self):
        self.assertFalse(self.e.abandoned["MT-02"])
        self.assertEqual(self.e.settled["CT-02"].status, "SETTLED")

    def test_pools_are_fully_paid_out(self):
        paid = sum(s.prize for s, _ in self.e.settled["CT-02"].standings)
        self.assertEqual(paid, 198 * 9900 * 85 // 100)


if __name__ == "__main__":
    unittest.main()
