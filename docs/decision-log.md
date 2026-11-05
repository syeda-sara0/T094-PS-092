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

## D-09 Few entries in a contest
If there are fewer entries than prize ranks, the percent of the unused ranks
is spread over the ranks that exist. Example: 1 entry wins the whole pool.

## D-10 Ties
Tied entries share the same rank (1, 2, 2, 2, 5).
The prizes of all ranks the tie covers are added, then split equally.
Extra paise go to the earliest submission, one paisa each.

## D-11 Band percent
Each band stores the TOTAL percent. Ranks 4-10 at 3% each is stored as 21.

## D-12 Abandoned match
Total legal balls of both innings below 120 (20 overs) means cancelled and refunded.

## D-13 TDS
TDS = 30% of positive cumulative net winnings, minus TDS already deducted.
Payouts are processed in time order.

## D-14 Entry lock
An entry is accepted if it is submitted at or before match start minus 1 minute.
One second later is rejected. An edit after the lock is rejected.

## D-15 Substitute (brief BR-02 is not detailed)
A listed player who did not play is replaced by the announced substitute at 0.5 weight.
If the substitute is already in the same team, the replaced slot gives 0, so he is not counted twice.
TO CHECK against the Week 2 sample output: does the substitute get the +4 playing-XI bonus,
and does a captain or vice-captain multiplier move to the substitute?

## D-16 Credits
Credits use Decimal. A team with exactly 100.0 credits is valid.
Exactly 7 players from one real team is valid.

## D-17 Ties
Default is to share the combined prize equally (brief BR-08).
The tie-break by earlier submission is needed only when tie-splitting is switched off. TO BUILD LATER.