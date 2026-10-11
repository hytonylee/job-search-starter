# Mode: pipeline

Reads: nothing. Run the script and use its output instead of opening `applications/PIPELINE.md`.

1. Run `python3 scripts/pipeline.py --html`.
2. Show me the terminal output as is.
3. Tell me the visual version is at `output/pipeline.html` (I open it in a browser, or run the script with `--open`).
4. If any row is flagged **overdue** or **no reply**, ask what I want to do about each one.

If Python is not available, read `applications/PIPELINE.md` and print the same summary by hand.

## The table format the script expects

- The header row starts with `Company` and keeps these columns: Company, Role, Stage, Applied, Last contact, Next action, Due, Source.
- Dates are `YYYY-MM-DD`.
- Stage is one of: Drafted, Applied, Screen, Technical, Final, Offer, Rejected, Withdrawn, No reply.
