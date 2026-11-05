from decimal import Decimal
from datetime import timedelta

MAX_CREDITS = Decimal("100.0")
TEAM_SIZE = 11
MAX_FROM_ONE_TEAM = 7
MAX_TEAMS_PER_USER = 6
# role: (minimum, maximum)
ROLE_LIMITS = {"WK": (1, 4), "BAT": (3, 6), "AR": (1, 4), "BOWL": (3, 6)}


def validate_team(players, captain, vice_captain):
    """players = list of dicts with keys: id, team, role, credit.
    Returns a list of error messages. An empty list means the team is valid."""
    errors = []
    ids = [p["id"] for p in players]

    if len(players) != TEAM_SIZE:
        errors.append("Team must have exactly 11 players")
    if len(set(ids)) != len(ids):
        errors.append("Same player picked twice")

    total = sum((Decimal(str(p["credit"])) for p in players), Decimal("0"))
    if total > MAX_CREDITS:          # exactly 100.0 is allowed
        errors.append(f"Credits {total} are more than 100.0")

    for role, (low, high) in ROLE_LIMITS.items():
        count = sum(1 for p in players if p["role"] == role)
        if count < low or count > high:
            errors.append(f"{role} count {count} must be between {low} and {high}")

    teams = {}
    for p in players:
        teams[p["team"]] = teams.get(p["team"], 0) + 1
    for team, count in teams.items():
        if count > MAX_FROM_ONE_TEAM:    # exactly 7 is allowed
            errors.append(f"{count} players from {team}, maximum is 7")

    if captain == vice_captain:
        errors.append("Captain and vice-captain must be different")
    if captain not in ids or vice_captain not in ids:
        errors.append("Captain and vice-captain must be in the team")

    return errors


def can_add_entry(existing_entries_of_user):
    """A user may submit up to 6 teams per contest."""
    return existing_entries_of_user < MAX_TEAMS_PER_USER


def entry_open(submit_time, match_start):
    """Entries are accepted until match start minus 1 minute (included)."""
    return submit_time <= match_start - timedelta(minutes=1)


def substitute_slot_points(sub_points, sub_already_in_team):
    """Points for a slot whose listed player did not play.
    The announced substitute counts at 0.5 weight.
    If the substitute is already in the team, this slot gives 0
    so that the same player is not counted twice (decision D-15)."""
    if sub_already_in_team:
        return Decimal("0")
    return Decimal(str(sub_points)) * Decimal("0.5")