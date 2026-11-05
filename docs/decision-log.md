# Decision Log

Each line is a choice we made where the brief was not clear.
We will check all of these against the Week 2 sample output.

## D-01 Band edges
The lower edge of every band is included.
Example: economy exactly 5.0 gives +4 (the 5-6 band), not +6.
Example: strike rate exactly 130 gives +2, and exactly 70 gives 0.

## D-02 Top edges (exceptions)
Strike rate exactly 170 gives +4, because the +6 band is "above 170".
Economy exactly 12 gives -4, because the -6 band is "above 12".

## D-03 Duck
A duck needs the batter to be OUT for 0. Not out on 0 gives no penalty.
The penalty applies only to batters, wicketkeepers and all-rounders.

## D-04 Strike rate and economy minimums
Strike rate counts only after 10 balls faced.
Economy counts only after 2 overs (12 legal balls).

## D-05 Exact numbers
Strike rate and economy use exact fractions, not decimals, so there are no rounding errors.

## D-06 Run-outs
Indirect run-out: 3 points to each of the two fielders.
Run-outs give the bowler no wicket points.

## D-07 Order of bonuses
Base points, then +4 playing-XI bonus, then captain x2 or vice-captain x1.5.
Example: (58 + 4) x 2 = 124.

## D-08 Credits and money (planned)
Credits will use Decimal. Money will use whole paise.