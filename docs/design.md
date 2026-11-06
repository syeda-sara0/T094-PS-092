# Design Document - Fantasy Cricket Engine (T094-PS-092)

## 1. Flow
CREATE_CONTEST -> ENTRY (validate, accept or reject) -> LOCK -> INGEST_DELIVERIES -> SCORE_MATCH
-> SETTLE_CONTEST -> PRINT_PLAYER_POINTS / PRINT_LEADERBOARD / PRINT_PAYOUTS

## 2. Modules and entities
| Module | Entities and responsibility |
|---|---|
| loader | Match, Player, Lineup, Delivery, Contest, PrizeBand, UserRecord, EntryRow |
| scoring | Stats (per player counters), PlayerPoints (one output row) |
| teams | validate_team, lock_time, slot_points, team_score |
| prizes | Pool, Standing, validate_bands, rank_prizes, distribute |
| tds | Ledger (per user per financial year), Payout |
| engine | Engine: holds state and runs commands in order |
| report | CSV writers, money and points formatting |

## 3. Business rules with one example each
| Rule | Summary | Example |
|---|---|---|
| BR-01 Team | 11 players, credits at most 100.0, 1-4 WK, 3-6 BAT, 1-4 AR, 3-6 BOWL, at most 7 from one team, captain and vice-captain distinct | EN-0005: exactly 100.0 credits and 7 from MUM is valid |
| BR-02 Entries | up to 6 teams per user per contest (contest sets the limit), lock at start minus 1 minute, edit after lock rejected, substitute at 0.5 weight | EN-0002 edit at 19:32 is rejected; EN-0007 edit at 19:28:59 is accepted |
| BR-03 Batting | 1 per run, +1 four, +2 six, one milestone (30/50/100 = 4/8/16), duck -2 | 30 runs, 4 fours, 2 sixes: 30+4+4+4 = 42 |
| BR-04 Strike rate | 10 balls minimum, bands above 170 +6 ... below 50 -6 | 30 off 10 balls = SR 300 = +6 |
| BR-05 Bowling | 25 per wicket, +8 LBW or bowled, haul 3/4/5 = 4/8/16, +12 maiden, economy bands for 2+ overs | 2.0 overs, 10 runs: economy 5.0 = +4 |
| BR-06 Fielding | catch 8, +4 at 3 catches, stumping 12, direct run-out 12, indirect run-out 6 split | DL-0015: PL-013 and PL-014 get 3 each |
| BR-07 Multipliers | +4 playing XI first, then captain x2 or vice-captain x1.5 | (58 + 4) x 2 = 124 |
| BR-08 Ranking | points descending; ties share the combined prize, rounded down, residue to earliest | CT-01 ranks 2, 3, 4 tie: each gets one third of 28 percent |
| BR-09 Pool | fees minus 15 percent; guaranteed pool and PLATFORM_SUBSIDY; under 2 entries cancelled | CT-03: 1 entry, pool 1000.00, subsidy 575.85 |
| BR-10 Bands | rank bands, percentages sum to 100, checked at CREATE_CONTEST | CT-01: 25 + 15 + 10 + 7x3 + 90x0.322222 |
| BR-11 TDS | 30 percent on the increase of cumulative net winnings in the financial year | net -200, +400, +700 gives TDS 0, 120, 90 |
| BR-12 Abandoned | under 20 overs (120 legal balls) cancels and refunds | MT-02: 27 overs, scoring stands |

## 4. Order of calculation (for the viva)
1. batting + strike rate + bowling + economy + fielding
2. + 4 playing XI
3. x captain or vice-captain multiplier
4. sum of 11 slots = team score
5. rank with ties, pool, rank prizes (rounded down), tie split, TDS

## 5. Design choices
- Money in whole paise, points as exact Fractions, credits as Decimal: no float rounding errors.
- Bands and limits are named constants or data, each rule is one small function, so each can be tested alone.
- See decision-log.md for every open point.
