# Decision Log

Choices made where the brief was silent or unclear. Source "README" means the sample
data pack README of 10 SECONDS, which states these binding choices.

## Bands (source: README)
- D-01 Strike rate: above 170 +6; 150-170 +4; 130 to below 150 +2; 60-70 -2; 50 to below 60 -4; below 50 -6.
  The gap 70 to 130 gives 0. Example: SR exactly 170 gives +4, exactly 150 gives +4, exactly 130 gives +2.
- D-02 Strike rate 70 exactly falls in the "60-70" band and gives -2 (we read the band as closed at 70). TO CONFIRM with 10 SECONDS.
- D-03 Economy: below 5 +6; 5-6 +4; above 6 up to 7 +2; above 7 to below 10 0; 10-11 -2; above 11 up to 12 -4; above 12 -6.
  Example: economy exactly 5.0 gives +4 (EC-03).
- D-04 Strike-rate points need 10 balls faced and are not applied to the BOWL role. Economy needs 12 legal balls.
- D-05 All points are exact fractions (no floats), printed with 2 decimals.

## Scoring
- D-06 Duck: out for 0, only for BAT, WK and AR. Not out on 0 gives no penalty.
- D-07 Balls faced exclude wides. Bowler runs = runs off the bat + wides + no-balls; byes and leg-byes are excluded.
- D-08 Legal balls exclude wides and no-balls. A maiden is an over of 6 legal balls with 0 bowler runs.
- D-09 Run-outs give the bowler nothing. Indirect run-out: 6 split equally between the fielders listed (3 each). Direct hit: 12 to fielder1.
- D-10 Catch bonus +4 is given once, when a player has 3 or more catches.
- D-11 The wickets column counts bowler wickets only (bowled, LBW, caught, stumped).
- D-12 Order: batting_pts (runs + fours + sixes + one milestone + duck) and sr_pts are separate columns.
  Example EC-02: 30 runs off 10 balls = 42 batting + 6 SR + 4 playing XI = 52.

## Teams and entries
- D-13 Credits use Decimal. Exactly 100.0 credits and exactly 7 players from one real team are valid.
- D-14 An entry is accepted at or before match start minus 1 minute. One second later is rejected.
  An EDIT keeps the first submission time. An EDIT after the lock is rejected and the old team stands.
- D-15 Rejection reasons are single codes, checked in this order: ENTRY_LOCKED, UNKNOWN_CONTEST, UNKNOWN_USER,
  EDIT_WITHOUT_ACCEPTED_ENTRY, DUPLICATE_ENTRY_ID, TEAM_SIZE_INVALID, DUPLICATE_PLAYER, UNKNOWN_PLAYER,
  PLAYER_NOT_IN_MATCH, CREDITS_EXCEEDED, ROLE_LIMIT_VIOLATED, TOO_MANY_FROM_ONE_TEAM, CAPTAIN_VICE_INVALID,
  MAX_TEAMS_PER_USER, CONTEST_FULL. Result words: ACCEPTED, REJECTED. TO CONFIRM wording with 10 SECONDS.
- D-16 Commands run strictly in file order. 52 CT-01 entries come BEFORE CREATE_CONTEST in commands.txt
  (timestamps before 2026-10-15 10:00) and are rejected as UNKNOWN_CONTEST. TO CONFIRM with 10 SECONDS.
- D-17 Substitute: a team holding the replaced player gets 0.5 x the substitute's total in that slot.
  If the substitute is already in the team, that slot gives 0 (EC-08).
- D-18 The captain or vice-captain multiplier stays on the slot of a replaced player (0.5 x substitute total x multiplier).
  TO CONFIRM with 10 SECONDS (20 sample entries are affected).

## Prizes and TDS
- D-19 Pool = max(guaranteed pool, 85 percent of fees) for guaranteed contests, else 85 percent of fees, rounded down to the paisa.
  The shortfall is printed as PLATFORM_SUBSIDY on the screen.
- D-20 Percentages in prize_structure.csv are per rank and have 6 decimals, so the total is checked within 0.001 of 100.
- D-21 Every rank prize is rounded down to the paisa. If entries are fewer than prize ranks, the share of empty ranks is
  spread over the filled ranks in proportion to their percentages (EC-06: the single entrant gets the whole pool).
- D-22 Ties with tie_split true: tied entries share the best rank (1, 2, 2, 2, 5). The prizes of all covered ranks are added,
  split equally, rounded down, and all left-over paise go to the earliest submission (EC-05).
- D-23 Ties with tie_split false: earlier submission wins, every entry gets its own rank.
- D-24 Abandoned match: fewer than 120 legal balls in total (20 overs) cancels the contests and refunds fees.
  A non-guaranteed contest with fewer than 2 entries is cancelled. Cancelled contests have no leaderboard or payout rows.
- D-25 TDS: taxable increase = max(cumulative net - net already taxed, 0), TDS = 30 percent of it rounded half up to the paisa.
  Entry fees of a contest count at its own payout. net_paid = winnings - TDS. TO CONFIRM rounding with 10 SECONDS.
- D-26 payouts.csv has one row per user with at least one accepted entry in a settled contest, sorted by user id.
