import sys
sys.path.insert(0, "src")

from datetime import datetime
from decimal import Decimal
from teams import (validate_team, can_add_entry, entry_open,
                   substitute_slot_points)

ROLES = ["WK", "BAT", "BAT", "BAT", "BAT", "AR", "AR",
         "BOWL", "BOWL", "BOWL", "BOWL"]


def make_team(credits, teams):
    return [{"id": f"P{i}", "team": teams[i], "role": ROLES[i],
             "credit": credits[i]} for i in range(11)]


CREDITS_100 = ["10.0"] + ["9.0"] * 10          # adds up to exactly 100.0
SEVEN_ONE_TEAM = ["A"] * 7 + ["B"] * 4

# Edge case: credits exactly 100.0 and 7 players from one team -> valid
assert validate_team(make_team(CREDITS_100, SEVEN_ONE_TEAM), "P0", "P1") == []

# 100.1 credits -> invalid
over = ["10.1"] + ["9.0"] * 10
assert len(validate_team(make_team(over, SEVEN_ONE_TEAM), "P0", "P1")) == 1

# 8 players from one team -> invalid
eight = ["A"] * 8 + ["B"] * 3
assert len(validate_team(make_team(CREDITS_100, eight), "P0", "P1")) == 1

# Captain and vice-captain must be different
assert len(validate_team(make_team(CREDITS_100, SEVEN_ONE_TEAM), "P0", "P0")) == 1

# Up to 6 teams per user per contest
assert can_add_entry(5) is True
assert can_add_entry(6) is False

# Entries close 1 minute before the match start
start = datetime(2026, 11, 10, 19, 0, 0)
assert entry_open(datetime(2026, 11, 10, 18, 59, 0), start) is True
assert entry_open(datetime(2026, 11, 10, 18, 59, 1), start) is False

# Substitute counts at 0.5 weight
assert substitute_slot_points(60, False) == Decimal("30")
# Edge case: substitute already in the team -> this slot gives 0
assert substitute_slot_points(60, True) == Decimal("0")

print("All team tests passed")