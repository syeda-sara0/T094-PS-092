"""Player points from ball-by-ball events (business rules BR-03 to BR-07).

Order for one player:
  batting_pts + sr_pts + bowling_pts + economy_pts + fielding_pts + playing_xi_pts
Captain / vice-captain multipliers are applied later, on the team (teams.py).
All points are exact Fractions.
"""
from dataclasses import dataclass
from fractions import Fraction

NOT_LEGAL = ("WIDE", "NOBALL")          # these are not legal balls
BOWLER_WICKETS = ("BOWLED", "LBW", "CAUGHT", "STUMPED")  # run-out is excluded


@dataclass
class Stats:
    runs: int = 0
    balls: int = 0
    fours: int = 0
    sixes: int = 0
    out: bool = False
    wickets: int = 0
    lbw_bowled: int = 0
    maidens: int = 0
    runs_conceded: int = 0
    legal_balls: int = 0
    catches: int = 0
    stumpings: int = 0
    runout_pts: int = 0


@dataclass(frozen=True)
class PlayerPoints:
    match_id: str
    player_id: str
    runs: int
    balls: int
    fours: int
    sixes: int
    batting_pts: Fraction
    sr_pts: Fraction
    wickets: int
    bowling_pts: Fraction
    economy_pts: Fraction
    fielding_pts: Fraction
    playing_xi_pts: Fraction
    total: Fraction


# ---------- small rule functions (each one is easy to test) ----------

def milestone_bonus(runs):
    """Only the highest bonus counts."""
    if runs >= 100:
        return 16
    if runs >= 50:
        return 8
    if runs >= 30:
        return 4
    return 0


def strike_rate_points(runs, balls):
    """Needs at least 10 balls faced. Bands from the sample pack README."""
    if balls < 10:
        return 0
    sr = Fraction(runs * 100, balls)
    if sr > 170:
        return 6
    if sr >= 150:
        return 4
    if sr >= 130:
        return 2
    if sr > 70:
        return 0
    if sr >= 60:
        return -2
    if sr >= 50:
        return -4
    return -6


def haul_bonus(wickets):
    """Only the highest bonus counts."""
    if wickets >= 5:
        return 16
    if wickets >= 4:
        return 8
    if wickets >= 3:
        return 4
    return 0


def economy_points(runs_conceded, legal_balls):
    """Needs at least 2 overs (12 legal balls)."""
    if legal_balls < 12:
        return 0
    eco = Fraction(runs_conceded * 6, legal_balls)
    if eco < 5:
        return 6
    if eco <= 6:
        return 4
    if eco <= 7:
        return 2
    if eco < 10:
        return 0
    if eco <= 11:
        return -2
    if eco <= 12:
        return -4
    return -6


def batting_points(stats, role):
    """Returns (batting_pts, sr_pts). Duck: out for 0, not for bowlers.
    Strike-rate points are not applied to the BOWL role."""
    pts = stats.runs + stats.fours + 2 * stats.sixes + milestone_bonus(stats.runs)
    if stats.out and stats.runs == 0 and role in ("BAT", "WK", "AR"):
        pts -= 2
    sr = 0 if role == "BOWL" else strike_rate_points(stats.runs, stats.balls)
    return pts, sr


def bowling_points(stats):
    """Returns (bowling_pts, economy_pts)."""
    pts = (25 * stats.wickets + 8 * stats.lbw_bowled
           + haul_bonus(stats.wickets) + 12 * stats.maidens)
    return pts, economy_points(stats.runs_conceded, stats.legal_balls)


def fielding_points(stats):
    pts = 8 * stats.catches + 12 * stats.stumpings + stats.runout_pts
    if stats.catches >= 3:
        pts += 4
    return pts


# ---------- reading the deliveries ----------

def collect_stats(deliveries):
    """Turns the ball-by-ball rows into one Stats record per player."""
    stats = {}

    def get(player_id):
        if player_id not in stats:
            stats[player_id] = Stats()
        return stats[player_id]

    overs = {}  # (innings, over, bowler) -> [legal balls, runs conceded]
    for d in deliveries:
        legal = d.extras_type not in NOT_LEGAL

        batter = get(d.striker)
        batter.runs += d.runs_off_bat
        if d.extras_type != "WIDE":          # a wide is not a ball faced
            batter.balls += 1
        if d.runs_off_bat == 4:
            batter.fours += 1
        elif d.runs_off_bat == 6:
            batter.sixes += 1

        bowler = get(d.bowler)
        conceded = d.runs_off_bat + (d.extras_runs if d.extras_type in NOT_LEGAL else 0)
        bowler.runs_conceded += conceded
        if legal:
            bowler.legal_balls += 1
        slot = overs.setdefault((d.innings, d.over, d.bowler), [0, 0])
        slot[0] += 1 if legal else 0
        slot[1] += conceded

        if d.wicket_type:
            if d.player_out:
                get(d.player_out).out = True
            if d.wicket_type in BOWLER_WICKETS:
                bowler.wickets += 1
                if d.wicket_type in ("BOWLED", "LBW"):
                    bowler.lbw_bowled += 1
            if d.wicket_type == "CAUGHT" and d.fielder1:
                get(d.fielder1).catches += 1
            elif d.wicket_type == "STUMPED" and d.fielder1:
                get(d.fielder1).stumpings += 1
            elif d.wicket_type == "RUN_OUT":
                if d.run_out_direct:
                    if d.fielder1:
                        get(d.fielder1).runout_pts += 12
                else:
                    fielders = [f for f in (d.fielder1, d.fielder2) if f]
                    for f in fielders:       # +6 split between the fielders
                        get(f).runout_pts += 6 // len(fielders)

    for (_, _, bowler_id), (legal_balls, conceded) in overs.items():
        if legal_balls == 6 and conceded == 0:
            get(bowler_id).maidens += 1
    return stats


def total_legal_balls(deliveries):
    return sum(1 for d in deliveries if d.extras_type not in NOT_LEGAL)


def build_player_points(match_id, lineups, players, deliveries):
    """One PlayerPoints row for every player in the match lineup, sorted by id."""
    stats = collect_stats(deliveries)
    xi = {row.player_id: row.in_playing_xi for row in lineups}
    ids = sorted(set(xi) | set(stats))
    rows = []
    for pid in ids:
        s = stats.get(pid, Stats())
        role = players[pid].role if pid in players else "BAT"
        bat, sr = batting_points(s, role)
        bowl, eco = bowling_points(s)
        field = fielding_points(s)
        xi_pts = 4 if xi.get(pid, False) else 0
        total = Fraction(bat + sr + bowl + eco + field + xi_pts)
        rows.append(PlayerPoints(match_id, pid, s.runs, s.balls, s.fours, s.sixes,
                                 Fraction(bat), Fraction(sr), s.wickets, Fraction(bowl),
                                 Fraction(eco), Fraction(field), Fraction(xi_pts), total))
    return rows
