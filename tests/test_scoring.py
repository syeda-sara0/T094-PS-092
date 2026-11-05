import sys
sys.path.insert(0, "src")

from scoring import batting_points, bowling_points, fielding_points, final_points

# 40 runs off 20 balls, 4 fours, 2 sixes -> 58
assert batting_points(40, 20, 4, 2, False, "BAT") == 58

# Edge case: exactly 30 runs off 10 balls -> 30 + 4 bonus + 6 (SR 300) = 40
assert batting_points(30, 10, 0, 0, False, "BAT") == 40

# Duck: -2 for a batter, 0 for a bowler
assert batting_points(0, 3, 0, 0, True, "BAT") == -2
assert batting_points(0, 3, 0, 0, True, "BOWL") == 0

# Edge case: 2.0 overs, economy exactly 5.0 -> +4
assert bowling_points(0, 0, 0, 10, 12) == 4

# 4 overs, 20 runs, 1 maiden, 3 wickets (1 LBW) -> 103
assert bowling_points(3, 1, 1, 20, 24) == 103

# 3 catches -> 24 + 4 = 28
assert fielding_points(3, 0, 0, 0) == 28

# Captain: (58 + 4) x 2 = 124
assert final_points(58, True, True, False) == 124

print("All tests passed")  