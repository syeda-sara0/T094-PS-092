"""Writes the output CSV files in the exact column order required."""
import csv
import os
from fractions import Fraction

FILES = {
    "entry_validation.csv": ["entry_id", "action", "action_ts", "result", "reason"],
    "player_points.csv": ["match_id", "player_id", "runs", "balls", "fours", "sixes",
                          "batting_pts", "sr_pts", "wickets", "bowling_pts",
                          "economy_pts", "fielding_pts", "playing_xi_pts", "total"],
    "leaderboard.csv": ["contest_id", "rank", "entry_id", "user_id", "points",
                        "submitted_ts", "prize"],
    "payouts.csv": ["contest_id", "user_id", "winnings", "cum_winnings",
                    "cum_entry_fees", "cum_net", "taxable_increase", "tds", "net_paid"],
}


def money(paise):
    """4900 -> '49.00' (works for negative numbers too)."""
    sign = "-" if paise < 0 else ""
    paise = abs(paise)
    return f"{sign}{paise // 100}.{paise % 100:02d}"


def points(value):
    """Exact fraction printed with 2 decimals, half rounded up."""
    value = Fraction(value)
    sign = "-" if value < 0 else ""
    hundredths = (abs(value) * 100 + Fraction(1, 2)).__floor__()
    return f"{sign}{hundredths // 100}.{hundredths % 100:02d}"


def write_csv(out_dir, name, rows):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, name), "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(FILES[name])
        writer.writerows(rows)


def player_point_row(p):
    return [p.match_id, p.player_id, p.runs, p.balls, p.fours, p.sixes,
            points(p.batting_pts), points(p.sr_pts), p.wickets, points(p.bowling_pts),
            points(p.economy_pts), points(p.fielding_pts), points(p.playing_xi_pts),
            points(p.total)]


def leaderboard_row(contest_id, user_id, s):
    return [contest_id, s.rank, s.entry_id, user_id, points(s.points),
            s.submitted_ts, money(s.prize)]


def payout_row(p):
    return [p.contest_id, p.user_id, money(p.winnings), money(p.cum_winnings),
            money(p.cum_entry_fees), money(p.cum_net), money(p.taxable_increase),
            money(p.tds), money(p.net_paid)]
