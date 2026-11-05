import sys
sys.path.insert(0, "src")

from prizes import (validate_bands, prize_pool, is_abandoned,
                    distribute, tds_for_payout, DEFAULT_BANDS)

# Bands must add up to 100
assert validate_bands(DEFAULT_BANDS)
try:
    validate_bands([(1, 1, 50), (2, 10, 40)])
    assert False, "should have failed"
except ValueError:
    pass

# Pool: 10 entries x Rs 100, minus 15 percent = Rs 850 (85000 paise)
assert prize_pool(10000, 10)["pool"] == 85000

# Not guaranteed, only 1 entry: cancelled and refunded
assert prize_pool(10000, 1)["status"] == "CANCELLED"

# Guaranteed contest, under-filled: pool is the guaranteed amount
r = prize_pool(10000, 3, guaranteed=500000)
assert r["pool"] == 500000
assert r["subsidy"] == 500000 - 25500

# Guaranteed contest with 1 entry: the single entrant wins the whole pool
one = distribute(500000, [("A", 50, 1)])
assert one["A"] == (1, 500000)

# Abandoned match: 119 balls is abandoned, 120 balls (20 overs) is not
assert is_abandoned(119) is True
assert is_abandoned(120) is False

# Three-way tie across ranks 2, 3 and 4 (two bands)
entries = [("A", 100, 1), ("B", 90, 2), ("C", 90, 3), ("D", 90, 4)]
entries += [(f"U{i}", 80 - i, 5 + i) for i in range(96)]
result = distribute(1000000, entries)
assert result["A"] == (1, 250000)
# ranks 2+3+4 = 15% + 10% + 3% = 28% = 280000 paise, split in 3
assert result["B"] == (2, 93334)   # earliest gets the extra paisa
assert result["C"] == (2, 93333)
assert result["D"] == (2, 93333)

# TDS turning positive for the first time, then rising
assert tds_for_payout(30000, 50000, 0) == 0        # net is negative
assert tds_for_payout(90000, 50000, 0) == 12000    # net +400
assert tds_for_payout(120000, 50000, 12000) == 9000  # net +700: 210 - 120

print("All money tests passed")