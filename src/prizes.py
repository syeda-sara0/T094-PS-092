from fractions import Fraction

PLATFORM_FEE_PERCENT = 15
TDS_PERCENT = 30
MIN_BALLS_FOR_VALID_MATCH = 120  # 20 overs x 6 balls

# (first_rank, last_rank, TOTAL percent of the whole band)
# Example: ranks 4-10 with 3% each = 21% for the band.
DEFAULT_BANDS = [
    (1, 1, 25),
    (2, 2, 15),
    (3, 3, 10),
    (4, 10, 21),
    (11, 100, 29),
]


def validate_bands(bands):
    """Bands must start at rank 1, have no gaps, and add up to 100 percent."""
    total = Fraction(0)
    expected_first = 1
    for first, last, percent in bands:
        if first != expected_first or last < first:
            raise ValueError("Bands must start at rank 1 with no gaps or overlaps")
        if percent < 0:
            raise ValueError("Percent cannot be negative")
        total += Fraction(percent)
        expected_first = last + 1
    if total != 100:
        raise ValueError("Band percentages must add up to 100")
    return True


def prize_pool(entry_fee, num_entries, guaranteed=None):
    """All money is in whole paise. Returns status, pool and subsidy."""
    collected = entry_fee * num_entries
    actual = collected * (100 - PLATFORM_FEE_PERCENT) // 100

    if guaranteed is None:
        if num_entries < 2:
            return {"status": "CANCELLED", "pool": 0, "subsidy": 0}
        return {"status": "OK", "pool": actual, "subsidy": 0}

    if num_entries < 1:
        return {"status": "CANCELLED", "pool": 0, "subsidy": 0}
    pool = max(actual, guaranteed)
    subsidy = max(guaranteed - actual, 0)  # printed as PLATFORM_SUBSIDY
    return {"status": "OK", "pool": pool, "subsidy": subsidy}


def is_abandoned(total_legal_balls):
    """Fewer than 20 overs in total means abandoned."""
    return total_legal_balls < MIN_BALLS_FOR_VALID_MATCH


def rank_prize(rank, pool, bands):
    """Prize for one rank, as an exact fraction."""
    for first, last, percent in bands:
        if first <= rank <= last:
            return Fraction(pool) * Fraction(percent) / 100 / (last - first + 1)
    return Fraction(0)


def tie_groups(entries):
    """entries = list of (entry_id, score, submit_order).
    Returns a list of (first_rank, [tied entries]) from best to worst.
    Tied entries share the same first rank, so ranks go 1, 2, 2, 2, 5."""
    ordered = sorted(entries, key=lambda e: (-e[1], e[2]))
    groups = []
    position = 1
    i = 0
    while i < len(ordered):
        j = i
        while j < len(ordered) and ordered[j][1] == ordered[i][1]:
            j += 1
        groups.append((position, ordered[i:j]))
        position += j - i
        i = j
    return groups


def distribute(pool, entries, bands=DEFAULT_BANDS):
    """Returns {entry_id: (rank, prize_in_paise)}.
    A tied group adds up the prizes of all the ranks it covers and splits
    the total equally. Extra paise go to the earliest submissions."""
    groups = tie_groups(entries)
    n = len(entries)

    # If there are fewer entries than prize ranks, the unused percent
    # is spread over the ranks that exist (decision D-09).
    total_raw = sum(rank_prize(r, pool, bands) for r in range(1, n + 1))
    scale = Fraction(pool) / total_raw if total_raw else Fraction(0)

    result = {}
    for start, members in groups:
        size = len(members)
        group_total = sum(
            rank_prize(r, pool, bands) for r in range(start, start + size)
        ) * scale
        share = int(group_total / size)          # rounded down to the paise
        leftover = int(group_total) - share * size
        for index, member in enumerate(members):
            extra = 1 if index < leftover else 0
            result[member[0]] = (start, share + extra)
    return result


def tds_for_payout(total_winnings, total_fees, tds_already_deducted):
    """Cumulative TDS. 30 percent of positive net winnings,
    minus the TDS already taken before."""
    net = total_winnings - total_fees
    due_in_total = max(net, 0) * TDS_PERCENT // 100
    return max(due_in_total - tds_already_deducted, 0)


def rupees(paise):
    return f"{paise // 100}.{paise % 100:02d}"