"""Prize pool, rank bands and tie splitting (BR-08, BR-09, BR-10, BR-12).

All money is whole paise. Percentages are exact Fractions.
"""
import math
from dataclasses import dataclass
from fractions import Fraction

PLATFORM_FEE_PERCENT = 15
MIN_LEGAL_BALLS = 120          # 20 overs
PERCENT_TOLERANCE = Fraction(1, 1000)   # the CSV has 6 decimals, so allow a tiny gap


def validate_bands(bands):
    """Returns None if fine, else a reason. Bands must start at rank 1,
    have no gaps, and add up to 100 percent."""
    if not bands:
        return "NO_PRIZE_BANDS"
    expected = 1
    total = Fraction(0)
    for band in sorted(bands, key=lambda b: b.rank_from):
        if band.rank_from != expected or band.rank_to < band.rank_from:
            return "BANDS_NOT_CONTIGUOUS"
        total += band.pct_per_rank * (band.rank_to - band.rank_from + 1)
        expected = band.rank_to + 1
    if abs(total - 100) > PERCENT_TOLERANCE:
        return "PERCENT_NOT_100"
    return None


def is_abandoned(legal_balls):
    """Fewer than 20 overs in total means abandoned."""
    return legal_balls < MIN_LEGAL_BALLS


@dataclass(frozen=True)
class Pool:
    status: str      # OK or CANCELLED
    pool: int        # paise
    subsidy: int     # paise (PLATFORM_SUBSIDY)
    collected: int   # paise of entry fees


def prize_pool(contest, num_entries):
    collected = contest.entry_fee * num_entries
    net = collected * (100 - PLATFORM_FEE_PERCENT) // 100
    if contest.guaranteed:
        if num_entries < 1:
            return Pool("CANCELLED", 0, 0, collected)
        return Pool("OK", max(contest.guaranteed_pool, net),
                    max(contest.guaranteed_pool - net, 0), collected)
    if num_entries < 2:
        return Pool("CANCELLED", 0, 0, collected)
    return Pool("OK", net, 0, collected)


def rank_prizes(pool, bands, num_ranks):
    """Prize in paise for rank 1..num_ranks, each rounded down to the paisa.
    If there are fewer entries than prize ranks, the share of the empty ranks
    is given to the filled ranks in proportion to their percentages."""
    pct = []
    for band in sorted(bands, key=lambda b: b.rank_from):
        pct.extend([band.pct_per_rank] * (band.rank_to - band.rank_from + 1))
    total_pct = sum(pct, Fraction(0))
    filled = pct[:num_ranks]
    filled_pct = sum(filled, Fraction(0))
    if filled_pct == 0:
        return [0] * num_ranks
    scale = total_pct / filled_pct
    prizes = [math.floor(Fraction(pool) * p / 100 * scale) for p in filled]
    return prizes + [0] * (num_ranks - len(prizes))


@dataclass(frozen=True)
class Standing:
    rank: int
    entry_id: str
    points: Fraction
    submitted_ts: str
    prize: int      # paise


def distribute(pool, bands, entries, tie_split):
    """entries: list of (entry_id, points, submitted_ts_text, submitted_dt).
    Returns Standing rows ordered by rank.

    tie_split True : tied entries share the rank, the prizes of all ranks the
                     tie covers are added and split equally, rounded down to the
                     paisa, the left-over paise go to the earliest submission.
    tie_split False: ties are broken by earlier submission, every entry gets
                     its own rank and its own prize."""
    ordered = sorted(entries, key=lambda e: (-e[1], e[3], e[0]))
    prizes = rank_prizes(pool, bands, len(ordered))
    rows = []
    if not tie_split:
        for index, (eid, points, ts_text, _) in enumerate(ordered):
            rows.append(Standing(index + 1, eid, points, ts_text, prizes[index]))
        return rows

    start = 0
    while start < len(ordered):
        end = start
        while end < len(ordered) and ordered[end][1] == ordered[start][1]:
            end += 1
        size = end - start
        combined = sum(prizes[start:end])
        share = combined // size
        residue = combined - share * size
        for offset in range(size):
            eid, points, ts_text, _ = ordered[start + offset]
            prize = share + (residue if offset == 0 else 0)
            rows.append(Standing(start + 1, eid, points, ts_text, prize))
        start = end
    return rows
