# T094-PS-092 - Fantasy Cricket Contest Scoring and Prize Distribution Engine

Back-end engine (no UI) for a fantasy cricket platform. It reads CSV files and a
command file, then prints player points, team scores, leaderboards and payouts with TDS.

Team: Syeda Sara Fathima (1AT24CG090) and Syeda Annam (1AT24CG089), section CSD, team T094.

## Language
Python 3.10 or higher. No extra libraries are needed.

## How to run
From the project folder:

    python src/main.py data output

- `data` holds the input files and `commands.txt`.
- `output` is created and receives the four result files and the validation file.

The command file is read strictly line by line. Messages such as
`PLATFORM_SUBSIDY|CT-03|575.85` are printed on the screen.

## Output files
| File | Content |
|---|---|
| entry_validation.csv | one row per ENTRY command: ACCEPTED or REJECTED with a reason code |
| player_points.csv | per-player points breakdown, one row per player per match |
| leaderboard.csv | accepted entries by rank with points and prize |
| payouts.csv | one row per user per contest with cumulative TDS columns |

## How to run the tests
    python -m unittest discover -s tests

56 tests: rule boundaries, every edge case from the brief, and the planted
scenarios in the sample data.

## Folder structure
| Folder or file | Purpose |
|---|---|
| src/loader.py | reads the CSV files into typed records |
| src/scoring.py | player points from ball-by-ball events |
| src/teams.py | team rules, entry lock time, team score with captain and substitute |
| src/prizes.py | prize pool, rank bands, tie splitting |
| src/tds.py | cumulative TDS ledger |
| src/engine.py | runs the commands in order |
| src/report.py | writes the CSV files |
| tests/ | unit tests and sample data scenario tests |
| docs/ | design document and decision log |
| data/ | sample data pack from 10 SECONDS |

## Order of calculation
1. Player points = batting + strike rate + bowling + economy + fielding
2. Add 4 for the announced playing XI
3. Captain x2, vice-captain x1.5 (the +4 is added before the multiplier)
4. Team score = sum of the 11 slots
5. Rank, resolve ties, work out the pool, split the prizes by band
6. TDS per user on the increase of cumulative net winnings

See `docs/decision-log.md` for every choice made where the brief was not clear.

## Documents
- Design document: docs/design.pdf
- Decision log: docs/decision-log.md
- Demo video (5 min): <paste link here>

## Edge cases handled
Expected results are taken from the sample data pack README.

| Case | Expected result |
|---|---|
| Credits exactly 100.0 and 7 players from one team | Valid (EN-0005) |
| Batter with 30 runs off 10 balls | 30 + 4 + 4 + 4 + 6 = 48, plus 4 for the playing XI |
| Bowler with 2.0 overs at economy 5.0 | +4 (band 5 to 6) |
| Run-out shared by two fielders in one team | 3 + 3 |
| Three-way tie on ranks 2, 3 and 4 | One third of 28% of the pool each, residue to the earliest submission |
| Guaranteed contest with 1 entry | Entrant wins the whole pool, shortfall printed as PLATFORM_SUBSIDY |
| Cumulative net winnings turn positive | TDS on the whole positive net (USR-0008) |
| Substitute already in the team | The replaced slot gives 0 (EN-0407) |

All of these are covered by the tests in `tests/`.

## Assumptions
- Prize pool = the larger of the guaranteed pool and 85% of entry fees.
- Prizes of ranks with no entrant are shared among the filled ranks in proportion to their percentages.
- Money is stored exactly (not as floats). Prizes are rounded down to the paisa.
- Entries that come before their contest is created are rejected as UNKNOWN_CONTEST. We asked 10 SECONDS to confirm this.
- All other choices are listed in docs/decision-log.md.

## Known limitations
- Stretch goals (live leaderboard recomputation after each over, multi-match series contests) are not implemented. <edit if this is not true>

## Who did what
- Syeda Sara Fathima: <your part>
- Syeda Annam: <your part>