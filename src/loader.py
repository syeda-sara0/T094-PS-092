"""Reads the input CSV files and turns them into simple typed records.

Money is kept as whole paise (int). Percentages are exact Fractions.
Credits are Decimal. Nothing here uses floats.
"""
import csv
import os
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from fractions import Fraction

TS_FORMAT = "%Y-%m-%d %H:%M:%S"


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def parse_ts(text):
    return datetime.strptime(text.strip(), TS_FORMAT)


def to_paise(text):
    """'49.00' -> 4900. Exact, no float."""
    return int((Decimal(text.strip()) * 100).to_integral_value())


def to_bool(text):
    return text.strip().lower() == "true"


@dataclass(frozen=True)
class Match:
    match_id: str
    home_team: str
    away_team: str
    start_ts: datetime


@dataclass(frozen=True)
class Player:
    player_id: str
    name: str
    team: str
    role: str
    credits: Decimal


@dataclass(frozen=True)
class Lineup:
    match_id: str
    team_code: str
    player_id: str
    in_playing_xi: bool
    substitute_for: str  # empty string when not a substitute


@dataclass(frozen=True)
class Delivery:
    match_id: str
    innings: int
    over: int
    ball_seq: int
    striker: str
    bowler: str
    runs_off_bat: int
    extras_type: str
    extras_runs: int
    wicket_type: str
    player_out: str
    fielder1: str
    fielder2: str
    run_out_direct: bool


@dataclass(frozen=True)
class Contest:
    contest_id: str
    match_id: str
    name: str
    entry_fee: int          # paise
    max_entries: int
    guaranteed: bool
    guaranteed_pool: int    # paise
    max_teams_per_user: int
    tie_split: bool


@dataclass(frozen=True)
class PrizeBand:
    rank_from: int
    rank_to: int
    pct_per_rank: Fraction  # percent, e.g. Fraction(25) for 25 percent


@dataclass(frozen=True)
class UserRecord:
    user_id: str
    winnings: int   # paise, financial year before this file
    fees: int       # paise
    net_taxed: int  # paise, net on which TDS was already deducted


@dataclass(frozen=True)
class EntryRow:
    entry_id: str
    contest_id: str
    user_id: str
    action: str
    ts_text: str
    ts: datetime
    players: tuple
    captain: str
    vice_captain: str


class DataPack:
    """Everything loaded from the data folder."""

    def __init__(self, data_dir):
        path = lambda name: os.path.join(data_dir, name)

        self.matches = {}
        for r in read_csv(path("matches.csv")):
            self.matches[r["match_id"]] = Match(
                r["match_id"], r["home_team"], r["away_team"], parse_ts(r["start_ts"]))

        self.players = {}
        for r in read_csv(path("players.csv")):
            self.players[r["player_id"]] = Player(
                r["player_id"], r["player_name"], r["team_code"], r["role"],
                Decimal(r["credits"]))

        self.lineups = {}
        for r in read_csv(path("lineups.csv")):
            self.lineups.setdefault(r["match_id"], []).append(Lineup(
                r["match_id"], r["team_code"], r["player_id"],
                to_bool(r["in_playing_xi"]), r["substitute_for"].strip()))

        self.deliveries = {}
        for r in read_csv(path("deliveries.csv")):
            self.deliveries.setdefault(r["match_id"], []).append(Delivery(
                r["match_id"], int(r["innings"]), int(r["over"]), int(r["ball_seq"]),
                r["striker"], r["bowler"], int(r["runs_off_bat"] or 0),
                r["extras_type"].strip(), int(r["extras_runs"] or 0),
                r["wicket_type"].strip(), r["player_out"].strip(),
                r["fielder1"].strip(), r["fielder2"].strip(),
                to_bool(r["run_out_direct"])))

        self.contests = {}
        for r in read_csv(path("contests.csv")):
            self.contests[r["contest_id"]] = Contest(
                r["contest_id"], r["match_id"], r["contest_name"],
                to_paise(r["entry_fee"]), int(r["max_entries"]),
                to_bool(r["guaranteed"]), to_paise(r["guaranteed_pool"]),
                int(r["max_teams_per_user"]), to_bool(r["tie_split"]))

        self.bands = {}
        for r in read_csv(path("prize_structure.csv")):
            self.bands.setdefault(r["contest_id"], []).append(PrizeBand(
                int(r["rank_from"]), int(r["rank_to"]), Fraction(r["pct_per_rank"])))

        self.users = {}
        for r in read_csv(path("users.csv")):
            self.users[r["user_id"]] = UserRecord(
                r["user_id"], to_paise(r["fy_winnings_before"]),
                to_paise(r["fy_entry_fees_before"]), to_paise(r["fy_net_taxed_before"]))

        self.entry_rows = {}
        for r in read_csv(path("entries.csv")):
            key = (r["entry_id"], r["action"], r["action_ts"])
            self.entry_rows[key] = EntryRow(
                r["entry_id"], r["contest_id"], r["user_id"], r["action"],
                r["action_ts"], parse_ts(r["action_ts"]),
                tuple(p.strip() for p in r["players"].split(";")),
                r["captain"].strip(), r["vice_captain"].strip())
