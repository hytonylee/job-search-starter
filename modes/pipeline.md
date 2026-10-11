# Mode: pipeline

Purpose: Show every application and its status.

Reads: nothing. Run the script and use its output instead of opening `applications/PIPELINE.md`.

1. Run `python3 scripts/pipeline.py --html`.
2. Show me the terminal output as is.
3. Tell me the visual version is at `output/pipeline.html` (I open it in a browser, or run the script with `--open`).
4. If any row is flagged **overdue** or **no reply**, ask what I want to do about each one.

If Python is not available, read `applications/PIPELINE.md` and print the same summary by hand.

## The table format the script expects

- The header row starts with `Company` and keeps these columns: Company, Role, Stage, Furthest, Applied, Last contact, Next action, Due, Source.
- Dates are `YYYY-MM-DD`.
- Stage is one of: Drafted, Applied, Screen, Interview, Final, Offer, Rejected, Withdrawn, No reply.
- If the table has no Furthest column (a file from an earlier version), add one after Stage, in the header, the separator and every row.
- Furthest is blank while a row is open. When you close a row (Rejected, Withdrawn, No reply), write the stage it had reached there, so the progress totals keep the interview or offer.
