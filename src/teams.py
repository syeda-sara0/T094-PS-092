"""Team rules (BR-01, BR-02) and team scoring (BR-07).

validate_team() returns None when the team is fine, otherwise a reason code.
"""
from datetime import timedelta
from decimal import Decimal
from fractions import Fraction

MAX_CREDITS = Decimal("100.0")
TEAM_SIZE = 11
MAX_FROM_ONE_TEAM = 7
ROLE_LIMITS = {"WK": (1, 4), "BAT": (3, 6), "AR": (1, 4), "BOWL": (3, 6)}
LOCK_BEFORE_START = timedelta(minutes=1)
SUBSTITUTE_WEIGHT = Fraction(1, 2)
CAPTAIN_MULTIPLIER = Fraction(2)
VICE_MULTIPLIER = Fraction(3, 2)


def lock_time(match_start):
    """Entries are accepted up to match start minus 1 minute (included)."""
    return match_start - LOCK_BEFORE_START


def validate_team(player_ids, captain, vice_captain, players, match_teams):
    """players: dict id -> Player. match_teams: the two team codes of the match."""
    if len(player_ids) != TEAM_SIZE:
        return "TEAM_SIZE_INVALID"
    if len(set(player_ids)) != len(player_ids):
        return "DUPLICATE_PLAYER"
    if any(pid not in players for pid in player_ids):
        return "UNKNOWN_PLAYER"
    chosen = [players[pid] for pid in player_ids]
    if any(p.team not in match_teams for p in chosen):
        return "PLAYER_NOT_IN_MATCH"
    if sum((p.credits for p in chosen), Decimal("0")) > MAX_CREDITS:
        return "CREDITS_EXCEEDED"       # exactly 100.0 is allowed
    for role, (low, high) in ROLE_LIMITS.items():
        count = sum(1 for p in chosen if p.role == role)
        if count < low or count > high:
            return "ROLE_LIMIT_VIOLATED"
    per_team = {}
    for p in chosen:
        per_team[p.team] = per_team.get(p.team, 0) + 1
    if max(per_team.values()) > MAX_FROM_ONE_TEAM:   # exactly 7 is allowed
        return "TOO_MANY_FROM_ONE_TEAM"
    if captain == vice_captain or captain not in player_ids or vice_captain not in player_ids:
        return "CAPTAIN_VICE_INVALID"
    return None


def substitute_map(lineups):
    """{listed player id: announced substitute id} for one match."""
    return {row.substitute_for: row.player_id for row in lineups if row.substitute_for}


def slot_points(player_id, team_ids, points, substitutes):
    """Points of one slot before captain / vice-captain multiplier.

    A listed player who was replaced gives 0.5 x the substitute's points,
    unless the substitute is already in the same team (then 0)."""
    if player_id in substitutes:
        sub_id = substitutes[player_id]
        if sub_id in team_ids:
            return Fraction(0)
        return SUBSTITUTE_WEIGHT * points[sub_id].total
    return points[player_id].total


def team_score(player_ids, captain, vice_captain, points, substitutes):
    """Sum of 11 slots. The +4 playing-XI bonus is already inside each
    player's total, so it is added BEFORE the multiplier."""
    team_ids = set(player_ids)
    score = Fraction(0)
    for pid in player_ids:
        value = slot_points(pid, team_ids, points, substitutes)
        if pid == captain:
            value *= CAPTAIN_MULTIPLIER
        elif pid == vice_captain:
            value *= VICE_MULTIPLIER
        score += value
    return score
