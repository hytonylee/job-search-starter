# Mode: archive

Purpose: Move old log entries and closed applications out of the way.

Run about once a month, or when `progress/daily-log.md` or the pipeline gets long. Reads: nothing.

1. Run `python3 scripts/archive.py`. This is a dry run and changes nothing.
2. Show me what it would move and ask me to confirm.
3. Only after I say yes, run `python3 scripts/archive.py --apply`.
4. Run `python3 scripts/pipeline.py` and show me the pipeline that remains.

## What it moves

- Daily-log entries older than 30 days go to `progress/_archive/daily-log-[year].md`.
- Pipeline rows that are Rejected, Withdrawn or No reply, last touched more than 30 days ago, go to `applications/_archive/PIPELINE-ARCHIVE.md`.
- `--days N` changes the 30.

## Rules

- Company folders stay where they are. Their interview notes still feed `progress/weak-spots.md`.
- Do not read the archive files in normal sessions. Open one only if I ask about something old.
- A closed row with no `YYYY-MM-DD` date is left in place. Fix its date, then run again.
- Only log sections headed `## YYYY-MM-DD` are archived. An entry ends at the next `#` or `##` heading, and a section with any other heading stays in the log.
