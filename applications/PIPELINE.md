# Pipeline

One row per application. A row is added as **Drafted** and moves to **Applied** only after I confirm I submitted it.

Stages: Drafted → Applied → Screen → Interview → Final → Offer, and to close a row: Rejected, Withdrawn, or No reply (after 21 days).

- **Screen** is the first call, usually with a recruiter. **Interview** is any round after that. **Final** is the last round.
- **Fit** is how many of the posting's required items I meet with evidence, out of how many it lists, written like `4/5`. It comes from the company's `fit.md`.
- **Furthest** is the furthest stage a row reached. Fill it in when a row is closed, so the interview or offer still counts. Leave it blank while the row is open.
- Dates are YYYY-MM-DD. Keep the column names as they are: `scripts/pipeline.py` reads this table. To view it, type `pipeline`, open the dashboard, or run `python3 scripts/pipeline.py --open`.

| Company | Role | Fit | Stage | Furthest | Applied | Last contact | Next action | Due | Source |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | |

## Weekly numbers

Updated every Friday during `check in`.

| Week of | Applied | Screens | Interviews | Offers | Reply rate |
|---|---|---|---|---|---|
| | | | | | |
