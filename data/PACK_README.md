# PS-092 – Fantasy Cricket Contest Scoring and Prize Distribution Engine — Sample Data Pack

Prepared by 10 SECONDS for Team T094.

## Files

| File | What it holds | Row count |
|---|---|---|
| `matches.csv` | 2 T20 matches with start time | 2 data rows |
| `players.csv` | Player pool (45: 4 squads of 11 plus one KOL reserve) with role and credits | 45 data rows |
| `lineups.csv` | Announced playing XI per match; the KOL reserve replaces a listed batter | 45 data rows |
| `deliveries.csv` | Ball-by-ball events for both matches (wides and no-balls are separate rows) | 417 data rows |
| `contests.csv` | 3 contests: fee, size, guaranteed pool, tie-split flag | 3 data rows |
| `prize_structure.csv` | Prize share per rank band (sums to 100% per contest) | 11 data rows |
| `users.csv` | Users with financial-year winnings / entry fees before this file | 150 data rows |
| `entries.csv` | Team submissions and edits (~600 entries) | 607 data rows |
| `commands.txt` | Contest creation, entries, locks, scoring, settlement and prints | 625 command lines (excluding comments) |

Row numbers quoted below are 1-based data-row numbers (the header is row 0). Line numbers for `commands.txt` are physical line numbers including comment lines.

## Column reference

Conventions: dates `YYYY-MM-DD`; timestamps `YYYY-MM-DD HH:MM:SS` (24h, IST, no timezone suffix); money in Rs as plain decimals with 2 places (no commas, no symbol); percentages as plain numbers (12.5 means 12.5%); booleans `true`/`false`; IDs uppercase with a fixed prefix. An empty cell means "not applicable" and only occurs in columns whose notes say so.

### `matches.csv`

| Column | Type | Units / format | Allowed values | Notes |
|---|---|---|---|---|
| match_id | string | MT-nn | — | — |
| home_team | string | — | MUM, CHE, BLR, KOL | — |
| away_team | string | — | — | — |
| start_ts | timestamp | — | — | entries lock 1 minute earlier |
| venue | string | — | — | — |
| overs_per_side | int | — | 20 | — |

### `players.csv`

| Column | Type | Units / format | Allowed values | Notes |
|---|---|---|---|---|
| player_id | string | PL-nnn | — | — |
| player_name | string | — | — | — |
| team_code | string | — | — | — |
| role | enum | — | WK, BAT, AR, BOWL | — |
| credits | decimal | — | — | 1 decimal |

### `lineups.csv`

| Column | Type | Units / format | Allowed values | Notes |
|---|---|---|---|---|
| match_id | string | — | matches.csv | — |
| team_code | string | — | — | — |
| player_id | string | — | players.csv | — |
| in_playing_xi | bool | — | — | +4 points if true |
| substitute_for | string | — | players.csv | set on the announced substitute: the listed player he replaces |

### `deliveries.csv`

| Column | Type | Units / format | Allowed values | Notes |
|---|---|---|---|---|
| delivery_id | string | DL-nnnn | — | — |
| match_id | string | — | — | — |
| innings | int | — | 1, 2 | — |
| over | int | — | 0-19 | 0-based |
| ball_seq | int | — | — | delivery number within the over incl. wides/no-balls |
| batting_team | string | — | — | — |
| striker | string | — | players.csv | — |
| non_striker | string | — | players.csv | — |
| bowler | string | — | players.csv | — |
| runs_off_bat | int | — | — | 4 / 6 = boundary |
| extras_type | enum | — | WIDE, NOBALL, BYE, LEGBYE | empty = none; wides/no-balls are not legal balls |
| extras_runs | int | — | — | — |
| wicket_type | enum | — | BOWLED, LBW, CAUGHT, STUMPED, RUN_OUT | — |
| player_out | string | — | — | — |
| fielder1 | string | — | — | catcher / keeper / run-out thrower |
| fielder2 | string | — | — | second fielder of an indirect run-out |
| run_out_direct | bool | — | — | RUN_OUT only |

### `contests.csv`

| Column | Type | Units / format | Allowed values | Notes |
|---|---|---|---|---|
| contest_id | string | CT-nn | — | — |
| match_id | string | — | matches.csv | — |
| contest_name | string | — | — | — |
| entry_fee | decimal | Rs | — | — |
| max_entries | int | — | — | — |
| guaranteed | bool | — | — | — |
| guaranteed_pool | decimal | Rs | — | 0.00 when not guaranteed |
| max_teams_per_user | int | — | — | — |
| tie_split | bool | — | — | false: ties broken by earlier submission |

### `prize_structure.csv`

| Column | Type | Units / format | Allowed values | Notes |
|---|---|---|---|---|
| contest_id | string | — | contests.csv | — |
| rank_from | int | — | — | — |
| rank_to | int | — | — | — |
| pct_per_rank | decimal | % | — | 6 decimals; band total = pct x ranks |

### `users.csv`

| Column | Type | Units / format | Allowed values | Notes |
|---|---|---|---|---|
| user_id | string | USR-nnnn | — | — |
| user_name | string | — | — | — |
| pan | string | PAN | — | — |
| fy_winnings_before | decimal | Rs | — | FY 2026-27 before this file |
| fy_entry_fees_before | decimal | Rs | — | — |
| fy_net_taxed_before | decimal | Rs | — | cumulative net on which TDS was already deducted |

### `entries.csv`

| Column | Type | Units / format | Allowed values | Notes |
|---|---|---|---|---|
| entry_id | string | EN-nnnn | — | an EDIT row reuses the entry_id |
| contest_id | string | — | contests.csv | — |
| user_id | string | — | users.csv | — |
| action | enum | — | SUBMIT, EDIT | — |
| action_ts | timestamp | — | — | submission timestamp = SUBMIT row's action_ts |
| players | string | 11 ids ';'-separated | — | — |
| captain | string | — | — | 2x |
| vice_captain | string | — | — | 1.5x |

## Command file format

`commands.txt` holds one command per line in the form `COMMAND_NAME|arg1|arg2|...`. Commands must be processed strictly in file order. Lines starting with `#` are comments and blank lines are ignored. An empty argument (two pipes in a row) means "not supplied". Every command used in this pack:

| Command | Arguments (in order) | Meaning |
|---|---|---|
| `CREATE_CONTEST` | `contest_id` | Create a contest; prize percentages must sum to 100 |
| `ENTRY` | `entry_id|SUBMIT or EDIT|timestamp` | Validate and accept / reject the entries.csv row |
| `LOCK` | `match_id` | Lock entries (match start - 1 minute) |
| `INGEST_DELIVERIES` | `match_id` | Load the match's deliveries |
| `SCORE_MATCH` | `match_id` | Player points and team scores |
| `SETTLE_CONTEST` | `contest_id` | Rank, distribute prizes, TDS, payouts |
| `PRINT_PLAYER_POINTS` | `match_id` | Per-player points breakdown |
| `PRINT_LEADERBOARD` | `contest_id` | Leaderboard |
| `PRINT_PAYOUTS` | `` | Payout file |

## Planted scenarios

Every edge case in the brief, mapped to the exact record where it occurs, followed by extra traps.

- **EC-01 Team with credits exactly 100.0 and 7 players from one team**
  - EN-0005: 11 players with credits summing to exactly 100.0 and 7 from MUM (the maximum from one team) -> VALID — `entries.csv EN-0005 (row 92) SUBMIT`
- **EC-02 Batter scoring exactly 30 runs off 10 balls - bonus plus SR band 300**
  - Batter PL-027 (MT-02, innings 1) scores exactly 30 off 10 balls (4 fours, 2 sixes, caught on his 10th ball): 30 runs + 4 + 4 (six bonus 2 x 2) + 4 (30-run bonus) + 6 (SR 300 > 170) = 48 batting points (+4 playing XI) — `players.csv PL-027 (row 27)`
- **EC-03 Bowler with 2.0 overs at economy exactly 5.0**
  - Bowler PL-019 (MT-01) bowls exactly 2.0 overs (overs 4 and 10) conceding 10 runs -> economy exactly 5.0 -> band 5-6 -> +4 (not the below-5 +6); he qualifies for economy points (>= 2 overs) — `players.csv PL-019 (row 19)`
- **EC-04 Run-out shared by two fielders who are both in a user's team**
  - DL-0015: indirect run-out of PL-003 by PL-013 and PL-014 -> +6 split 3 + 3; entry EN-0006 contains both fielders and gets both halves — `deliveries.csv DL-0015 (row 15); entries.csv EN-0006 (row 189) SUBMIT`
- **EC-05 Three-way tie across ranks 2, 3 and 4 spanning two prize bands**
  - CT-01: EN-0002, EN-0003 and EN-0004 submitted the identical team (same captain / vice-captain) and tie on ranks 2, 3 and 4, which span two prize bands (15% + 10% + 3%): each gets one third of 28% of the pool, rounded down to the paisa, residue to the earliest submission (EN-0002). Rank 1 is EN-0001 — `entries.csv EN-0001 (row 467) SUBMIT; entries.csv EN-0002 (row 480) SUBMIT; entries.csv EN-0003 (row 491) SUBMIT; entries.csv EN-0004 (row 499) SUBMIT`
- **EC-06 Guaranteed contest with 1 entry - single entrant wins whole pool**
  - CT-03 is guaranteed (pool Rs 1,000.00) and receives a single entry EN-0605 (fee 499 -> 424.15 after the 15% platform fee): the single entrant wins the whole guaranteed pool; shortfall Rs 575.85 printed as PLATFORM_SUBSIDY — `entries.csv EN-0605 (row 598) SUBMIT`
- **EC-07 User whose cumulative net winnings turn positive mid-year for the first time**
  - USR-0008: FY winnings 1,200.00 vs entry fees 3,000.00 before this file (net negative, nothing taxed); rank 1 in CT-01 (25% of the pool) makes the cumulative net positive for the first time -> TDS 30% on the whole positive net at the CT-01 payout — `users.csv USR-0008 (row 8); entries.csv EN-0001 (row 467) SUBMIT`
- **EC-08 Announced substitute who also appears in the user's team already**
  - EN-0407 contains both PL-037 (listed, replaced in the KOL playing XI) and PL-045 (the announced substitute, lineups.csv) -> no 0.5-weight substitute points for PL-037 (the substitute already scores in full); contrast EN-0408: has PL-037 without PL-045 -> gets 0.5 x PL-045's points — `entries.csv EN-0407 (row 434) SUBMIT; entries.csv EN-0408 (row 306) SUBMIT; lineups.csv MT-02 (row 45)`
- **Extra traps (not in the brief, but realistic):**
  - EN-0405: user USR-0007's 7th team in CT-01 -> REJECTED (max 6 per user) — `entries.csv EN-0405 (row 432) SUBMIT`
  - EN-0406: team of the 11 most expensive players -> credits above 100.0 -> REJECTED — `entries.csv EN-0406 (row 449) SUBMIT`
  - EN-0002: EDIT at match start + 2 min (after the lock at start - 1 min) -> REJECTED, the original team stands; EN-0007: EDIT 1 min 1 s before start -> accepted — `entries.csv EN-0002 (row 523) EDIT; entries.csv EN-0007 (row 522) EDIT`
  - MT-02 is rain-shortened: KOL's chase is stopped after 7 overs -> 27 overs bowled in total (>= 20) -> not abandoned, scoring stands on the events received — `matches.csv MT-02 (row 2)`

## What is NOT in this pack

Expected outputs are not provided for this set. Validate your engine with your own test suite against the rules in your brief (BR-01 … BR-nn). A separate hidden input set with the same schema will be used at final evaluation; outputs are compared field-for-field, so follow the column formats above exactly in your own output.

## Output format expected at evaluation

Produce these CSV files (header row, same conventions as above, rows sorted as stated). Where the brief is silent on a format detail the choice below is binding for evaluation.

### `entry_validation.csv`

One row per ENTRY.

Columns, in order: `entry_id`, `action`, `action_ts`, `result`, `reason`

### `player_points.csv`

One row per player per match.

Columns, in order: `match_id`, `player_id`, `runs`, `balls`, `fours`, `sixes`, `batting_pts`, `sr_pts`, `wickets`, `bowling_pts`, `economy_pts`, `fielding_pts`, `playing_xi_pts`, `total`

### `leaderboard.csv`

One row per accepted entry, by rank.

Columns, in order: `contest_id`, `rank`, `entry_id`, `user_id`, `points`, `submitted_ts`, `prize`

### `payouts.csv`

One row per user per contest settled.

Columns, in order: `contest_id`, `user_id`, `winnings`, `cum_winnings`, `cum_entry_fees`, `cum_net`, `taxable_increase`, `tds`, `net_paid`

Binding choices where the brief is silent: points are kept as exact fractions and printed with 2 decimals. SR bands: > 170 +6; 150-170 +4; 130-<150 +2; 60-70 -2; 50-<60 -4; < 50 -6 (not applied to BOWL role). Economy bands: < 5 +6; 5-6 +4; >6-7 +2; 10-11 -2; >11-12 -4; > 12 -6 (bowler runs = off the bat + wides + no-balls; byes/leg-byes excluded; balls faced exclude wides). Substitute: a team holding the replaced player gets 0.5 x the substitute's points in that slot unless the substitute is already in the team (then 0). Prize pool = max(guaranteed_pool, 0.85 x fees); prizes of ranks with no entrant are redistributed to the filled ranks in proportion to their percentages. Prizes rounded down to the paisa. TDS at each payout = 30% x (cum_net - fy_net_taxed so far) when positive; entry fees of a contest count at its own payout.
