"""Runs the command file, strictly in file order.

Commands: CREATE_CONTEST, ENTRY, LOCK, INGEST_DELIVERIES, SCORE_MATCH,
          SETTLE_CONTEST, PRINT_PLAYER_POINTS, PRINT_LEADERBOARD, PRINT_PAYOUTS
"""
from dataclasses import dataclass
from fractions import Fraction

import prizes
import report
import scoring
import teams
import tds
from loader import DataPack


@dataclass
class AcceptedEntry:
    entry_id: str
    user_id: str
    players: tuple
    captain: str
    vice_captain: str
    ts_text: str
    ts: object


@dataclass
class Settlement:
    status: str               # SETTLED or CANCELLED
    standings: list
    payouts: list


class Engine:
    def __init__(self, data_dir):
        self.data = DataPack(data_dir)
        self.created = {}          # contest_id -> Contest
        self.locked = set()        # match ids
        self.entries = {}          # contest_id -> {entry_id: AcceptedEntry}
        self.ingested = {}         # match_id -> deliveries
        self.points = {}           # match_id -> {player_id: PlayerPoints}
        self.point_rows = {}       # match_id -> [PlayerPoints] sorted
        self.abandoned = {}        # match_id -> bool
        self.scores = {}           # contest_id -> {entry_id: Fraction}
        self.settled = {}          # contest_id -> Settlement
        self.settle_order = []
        self.ledgers = {uid: tds.Ledger(u.winnings, u.fees, u.net_taxed)
                        for uid, u in self.data.users.items()}
        self.out_validation = []
        self.out_points = []
        self.out_leaderboard = []
        self.out_payouts = []

    # ---------------------------------------------------------- commands
    def run(self, commands_path):
        with open(commands_path, encoding="utf-8") as handle:
            for number, line in enumerate(handle, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                name, *args = line.split("|")
                handler = getattr(self, "cmd_" + name.lower(), None)
                if handler is None:
                    print(f"WARNING line {number}: unknown command {name}")
                    continue
                handler(*args)

    def cmd_create_contest(self, contest_id):
        contest = self.data.contests.get(contest_id)
        if contest is None:
            print(f"CONTEST_REJECTED|{contest_id}|UNKNOWN_CONTEST")
            return
        reason = prizes.validate_bands(self.data.bands.get(contest_id, []))
        if reason:
            print(f"CONTEST_REJECTED|{contest_id}|{reason}")
            return
        self.created[contest_id] = contest
        self.entries[contest_id] = {}

    def cmd_lock(self, match_id):
        self.locked.add(match_id)

    def cmd_entry(self, entry_id, action, ts_text):
        row = self.data.entry_rows.get((entry_id, action, ts_text))
        if row is None:
            self._validation(entry_id, action, ts_text, "REJECTED", "ENTRY_ROW_NOT_FOUND")
            return
        reason = self._check_entry(row)
        if reason is None:
            self._accept(row)
        self._validation(entry_id, action, ts_text,
                         "REJECTED" if reason else "ACCEPTED", reason or "")

    def cmd_ingest_deliveries(self, match_id):
        self.ingested[match_id] = self.data.deliveries.get(match_id, [])

    def cmd_score_match(self, match_id):
        if match_id not in self.ingested:
            print(f"ERROR|SCORE_MATCH|{match_id}|DELIVERIES_NOT_INGESTED")
            return
        deliveries = self.ingested[match_id]
        rows = scoring.build_player_points(
            match_id, self.data.lineups.get(match_id, []), self.data.players, deliveries)
        self.point_rows[match_id] = rows
        self.points[match_id] = {r.player_id: r for r in rows}
        self.abandoned[match_id] = prizes.is_abandoned(scoring.total_legal_balls(deliveries))
        subs = teams.substitute_map(self.data.lineups.get(match_id, []))
        for contest_id, contest in self.created.items():
            if contest.match_id != match_id:
                continue
            self.scores[contest_id] = {
                e.entry_id: teams.team_score(e.players, e.captain, e.vice_captain,
                                             self.points[match_id], subs)
                for e in self.entries[contest_id].values()}

    def cmd_settle_contest(self, contest_id):
        contest = self.created.get(contest_id)
        if contest is None or contest_id not in self.scores:
            print(f"ERROR|SETTLE_CONTEST|{contest_id}|NOT_CREATED_OR_NOT_SCORED")
            return
        accepted = self.entries[contest_id]
        pool = prizes.prize_pool(contest, len(accepted))
        cancelled = pool.status == "CANCELLED" or self.abandoned.get(contest.match_id, False)
        if cancelled:
            self.settled[contest_id] = Settlement("CANCELLED", [], [])
            self.settle_order.append(contest_id)
            print(f"CONTEST_CANCELLED|{contest_id}|REFUND|{report.money(pool.collected)}")
            return

        entry_list = [(e.entry_id, self.scores[contest_id][e.entry_id], e.ts_text, e.ts)
                      for e in accepted.values()]
        standings = prizes.distribute(pool.pool, self.data.bands[contest_id],
                                      entry_list, contest.tie_split)
        won, fee_count, owner = {}, {}, {}
        for s in standings:
            user = accepted[s.entry_id].user_id
            owner[s.entry_id] = user
            won[user] = won.get(user, 0) + s.prize
            fee_count[user] = fee_count.get(user, 0) + 1
        payouts = []
        for user in sorted(won):
            ledger = self.ledgers.setdefault(user, tds.Ledger(0, 0, 0))
            payouts.append(tds.settle_user(ledger, contest_id, user, won[user],
                                           fee_count[user] * contest.entry_fee))
        self.settled[contest_id] = Settlement("SETTLED", [(s, owner[s.entry_id]) for s in standings], payouts)
        self.settle_order.append(contest_id)
        if pool.subsidy:
            print(f"PLATFORM_SUBSIDY|{contest_id}|{report.money(pool.subsidy)}")

    def cmd_print_player_points(self, match_id):
        for p in self.point_rows.get(match_id, []):
            self.out_points.append(report.player_point_row(p))
        print(f"PLAYER_POINTS|{match_id}|{len(self.point_rows.get(match_id, []))} players")

    def cmd_print_leaderboard(self, contest_id):
        settlement = self.settled.get(contest_id)
        count = 0
        if settlement:
            for standing, user in settlement.standings:
                self.out_leaderboard.append(report.leaderboard_row(contest_id, user, standing))
                count += 1
        print(f"LEADERBOARD|{contest_id}|{count} rows")

    def cmd_print_payouts(self):
        count = 0
        for contest_id in self.settle_order:
            for payout in self.settled[contest_id].payouts:
                self.out_payouts.append(report.payout_row(payout))
                count += 1
        print(f"PAYOUTS|{count} rows")

    # ---------------------------------------------------------- entries
    def _validation(self, entry_id, action, ts_text, result, reason):
        self.out_validation.append([entry_id, action, ts_text, result, reason])

    def _check_entry(self, row):
        """Returns None if accepted, else a reason code. Checks run in this order."""
        contest = self.created.get(row.contest_id)
        if contest is None:
            return "UNKNOWN_CONTEST"
        match = self.data.matches[contest.match_id]
        if contest.match_id in self.locked or row.ts > teams.lock_time(match.start_ts):
            return "ENTRY_LOCKED"
        if row.user_id not in self.data.users:
            return "UNKNOWN_USER"
        existing = self.entries[row.contest_id]
        if row.action == "EDIT":
            original = existing.get(row.entry_id)
            if original is None or original.user_id != row.user_id:
                return "EDIT_WITHOUT_ACCEPTED_ENTRY"
        elif row.entry_id in existing:
            return "DUPLICATE_ENTRY_ID"
        reason = teams.validate_team(row.players, row.captain, row.vice_captain,
                                     self.data.players, (match.home_team, match.away_team))
        if reason:
            return reason
        if row.action == "SUBMIT":
            mine = sum(1 for e in existing.values() if e.user_id == row.user_id)
            if mine >= contest.max_teams_per_user:
                return "MAX_TEAMS_PER_USER"
            if len(existing) >= contest.max_entries:
                return "CONTEST_FULL"
        return None

    def _accept(self, row):
        existing = self.entries[row.contest_id]
        if row.action == "EDIT":
            original = existing[row.entry_id]     # keeps the first submission time
            existing[row.entry_id] = AcceptedEntry(
                row.entry_id, row.user_id, row.players, row.captain,
                row.vice_captain, original.ts_text, original.ts)
        else:
            existing[row.entry_id] = AcceptedEntry(
                row.entry_id, row.user_id, row.players, row.captain,
                row.vice_captain, row.ts_text, row.ts)

    # ---------------------------------------------------------- output
    def write_outputs(self, out_dir):
        report.write_csv(out_dir, "entry_validation.csv", self.out_validation)
        report.write_csv(out_dir, "player_points.csv", self.out_points)
        report.write_csv(out_dir, "leaderboard.csv", self.out_leaderboard)
        report.write_csv(out_dir, "payouts.csv", self.out_payouts)
