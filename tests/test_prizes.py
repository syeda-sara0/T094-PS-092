import unittest
from datetime import datetime, timedelta
from fractions import Fraction

import helpers
import prizes
import tds
from loader import Contest, PrizeBand

BANDS = [PrizeBand(1, 1, Fraction(25)), PrizeBand(2, 2, Fraction(15)),
         PrizeBand(3, 3, Fraction(10)), PrizeBand(4, 10, Fraction(3)),
         PrizeBand(11, 100, Fraction(29, 90))]


def contest(guaranteed=False, pool=0, fee=10000, tie=True):
    return Contest("C", "M", "n", fee, 500, guaranteed, pool, 6, tie)


def entries(scores):
    """scores: list of points in submission order -> engine style tuples."""
    base = datetime(2026, 1, 1)
    return [(f"E{i + 1}", Fraction(s), str(i), base + timedelta(minutes=i))
            for i, s in enumerate(scores)]


class BandTests(unittest.TestCase):
    def test_valid_bands(self):
        self.assertIsNone(prizes.validate_bands(BANDS))

    def test_bands_not_100(self):
        bad = [PrizeBand(1, 1, Fraction(50)), PrizeBand(2, 10, Fraction(4))]
        self.assertEqual(prizes.validate_bands(bad), "PERCENT_NOT_100")

    def test_bands_with_gap(self):
        bad = [PrizeBand(1, 1, Fraction(50)), PrizeBand(3, 4, Fraction(25))]
        self.assertEqual(prizes.validate_bands(bad), "BANDS_NOT_CONTIGUOUS")

    def test_csv_rounding_is_tolerated(self):
        csv_style = [PrizeBand(1, 1, Fraction("25")), PrizeBand(2, 2, Fraction("15")),
                     PrizeBand(3, 3, Fraction("10")), PrizeBand(4, 10, Fraction("3")),
                     PrizeBand(11, 100, Fraction("0.322222"))]
        self.assertIsNone(prizes.validate_bands(csv_style))


class PoolTests(unittest.TestCase):
    def test_pool_minus_15_percent(self):
        p = prizes.prize_pool(contest(fee=4900), 352)
        self.assertEqual((p.status, p.pool), ("OK", 1466080))

    def test_non_guaranteed_under_2_entries_cancelled(self):
        self.assertEqual(prizes.prize_pool(contest(), 1).status, "CANCELLED")
        self.assertEqual(prizes.prize_pool(contest(), 2).status, "OK")

    def test_guaranteed_shortfall_is_subsidy(self):
        p = prizes.prize_pool(contest(guaranteed=True, pool=100000, fee=49900), 1)
        self.assertEqual((p.pool, p.subsidy), (100000, 100000 - 42415))

    def test_abandoned_boundary(self):
        self.assertTrue(prizes.is_abandoned(119))
        self.assertFalse(prizes.is_abandoned(120))


class DistributeTests(unittest.TestCase):
    def test_edge_three_way_tie_over_ranks_2_3_4(self):
        scores = [100, 90, 90, 90] + [80 - i for i in range(96)]
        rows = prizes.distribute(1000000, BANDS, entries(scores), True)
        by = {r.entry_id: r for r in rows}
        self.assertEqual((by["E1"].rank, by["E1"].prize), (1, 250000))
        # ranks 2+3+4 = 15% + 10% + 3% = 28% = 280000, split in 3, residue to earliest
        self.assertEqual([by[e].rank for e in ("E2", "E3", "E4")], [2, 2, 2])
        self.assertEqual([by[e].prize for e in ("E2", "E3", "E4")], [93334, 93333, 93333])
        self.assertEqual(by["E5"].rank, 5)

    def test_residue_all_goes_to_earliest(self):
        # 3 tied for ranks 2,3,4 with a pool where 28% is not divisible by 3
        scores = [100, 90, 90, 90] + [80 - i for i in range(96)]
        rows = prizes.distribute(1000001, BANDS, entries(scores), True)
        tied = [r.prize for r in rows if r.rank == 2]
        combined = sum(prizes.rank_prizes(1000001, BANDS, 100)[1:4])
        self.assertEqual(sum(tied), combined)
        self.assertEqual(tied[1], tied[2])
        self.assertGreaterEqual(tied[0], tied[1])

    def test_tie_split_off_earlier_submission_wins(self):
        rows = prizes.distribute(1000000, BANDS, entries([50, 50, 50]), False)
        self.assertEqual([r.rank for r in rows], [1, 2, 3])
        self.assertEqual([r.entry_id for r in rows], ["E1", "E2", "E3"])

    def test_edge_guaranteed_contest_with_one_entry_wins_whole_pool(self):
        two_bands = [PrizeBand(1, 1, Fraction(60)), PrizeBand(2, 2, Fraction(40))]
        rows = prizes.distribute(100000, two_bands, entries([406]), True)
        self.assertEqual(rows[0].prize, 100000)

    def test_empty_ranks_are_redistributed_in_proportion(self):
        two_bands = [PrizeBand(1, 1, Fraction(60)), PrizeBand(2, 2, Fraction(40))]
        prizes_list = prizes.rank_prizes(100000, two_bands, 2)
        self.assertEqual(prizes_list, [60000, 40000])
        three = prizes.rank_prizes(100000, BANDS, 3)
        self.assertEqual(three, [50000, 30000, 20000])   # 25:15:10 scaled to 100 percent


class TdsTests(unittest.TestCase):
    def test_edge_net_turns_positive_mid_year(self):
        # net -200 (nothing taxed), then +400 (TDS 120), then +700 (TDS 90)
        ledger = tds.Ledger(winnings=0, fees=0, net_taxed=0)
        a = tds.settle_user(ledger, "C1", "U", 0, 20000)
        self.assertEqual((a.cum_net, a.tds), (-20000, 0))
        b = tds.settle_user(ledger, "C2", "U", 60000, 0)
        self.assertEqual((b.cum_net, b.taxable_increase, b.tds), (40000, 40000, 12000))
        c = tds.settle_user(ledger, "C3", "U", 30000, 0)
        self.assertEqual((c.cum_net, c.taxable_increase, c.tds), (70000, 30000, 9000))
        self.assertEqual(c.net_paid, 21000)

    def test_first_time_positive_taxes_whole_net(self):
        ledger = tds.Ledger(winnings=120000, fees=300000, net_taxed=0)
        p = tds.settle_user(ledger, "C", "U", 366520 + 9000, 4900)
        self.assertEqual(p.taxable_increase, p.cum_net)
        self.assertEqual(p.tds, (p.cum_net * 30 + 50) // 100)

    def test_no_double_tax_when_net_falls(self):
        ledger = tds.Ledger(winnings=600000, fees=120000, net_taxed=480000)
        p = tds.settle_user(ledger, "C", "U", 0, 5000)
        self.assertEqual((p.taxable_increase, p.tds), (0, 0))
        q = tds.settle_user(ledger, "C2", "U", 5000, 0)    # back to the old net: still no tax
        self.assertEqual(q.tds, 0)


if __name__ == "__main__":
    unittest.main()
