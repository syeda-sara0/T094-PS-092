# Design Document - Fantasy Cricket Engine

## Order of calculation
1. Player base points = batting + bowling + fielding
2. Add +4 playing-XI bonus
3. Multiply: captain x2, vice-captain x1.5
4. Team score = sum of the 11 final player points
5. Rank teams and resolve ties
6. Prize pool, prize bands, split tied prizes
7. TDS per user

## Worked example
Batter: 40 runs off 20 balls, 4 fours, 2 sixes.
40 runs + 4 (fours) + 4 (sixes) + 4 (30-run milestone) + 6 (strike rate 200) = 58.
If captain: (58 + 4) x 2 = 124.