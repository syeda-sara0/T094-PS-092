from fractions import Fraction
from decimal import Decimal


def batting_points(runs, balls, fours, sixes, is_out, role):
    """Points a batter earns. role is BAT, WK, AR or BOWL."""
    points = runs + fours * 1 + sixes * 2

    # Only the highest milestone bonus counts
    if runs >= 100:
        points += 16
    elif runs >= 50:
        points += 8
    elif runs >= 30:
        points += 4

    # Duck: out for 0, only for BAT, WK, AR
    if runs == 0 and is_out and role in ("BAT", "WK", "AR"):
        points -= 2

    # Strike rate counts only if the batter faced at least 10 balls
    if balls >= 10:
        sr = Fraction(runs * 100, balls)
        if sr > 170:
            points += 6
        elif sr >= 150:
            points += 4
        elif sr >= 130:
            points += 2
        elif sr >= 70:
            points += 0
        elif sr >= 60:
            points -= 2
        elif sr >= 50:
            points -= 4
        else:
            points -= 6

    return points


def bowling_points(wickets, lbw_bowled, maidens, runs_conceded, legal_balls):
    """Points a bowler earns. wickets must NOT include run-outs."""
    points = wickets * 25 + lbw_bowled * 8 + maidens * 12

    # Only the highest haul bonus counts
    if wickets >= 5:
        points += 16
    elif wickets >= 4:
        points += 8
    elif wickets >= 3:
        points += 4

    # Economy counts only if the bowler bowled at least 2 overs (12 balls)
    if legal_balls >= 12:
        economy = Fraction(runs_conceded * 6, legal_balls)
        if economy < 5:
            points += 6
        elif economy < 6:
            points += 4
        elif economy < 7:
            points += 2
        elif economy < 10:
            points += 0
        elif economy < 11:
            points -= 2
        elif economy <= 12:
            points -= 4
        else:
            points -= 6

    return points


def fielding_points(catches, stumpings, direct_runouts, indirect_runouts):
    """indirect_runouts is the number of shared run-outs (3 points each)."""
    points = catches * 8 + stumpings * 12
    points += direct_runouts * 12 + indirect_runouts * 3
    if catches >= 3:
        points += 4
    return points


def final_points(base, in_playing_xi, is_captain, is_vice_captain):
    """+4 is added first, then the multiplier."""
    total = Decimal(base)
    if in_playing_xi:
        total += 4
    if is_captain:
        total *= 2
    elif is_vice_captain:
        total *= Decimal("1.5")
    return total