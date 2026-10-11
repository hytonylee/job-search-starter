#!/usr/bin/env python3
"""Move old daily-log entries and closed applications into archive files.

Usage:
  python3 scripts/archive.py            show what would move, change nothing
  python3 scripts/archive.py --apply    move it
  python3 scripts/archive.py --days 14  use a 14 day cut-off instead of 30

What moves:
  - Entries in progress/daily-log.md dated more than --days ago go to
    progress/_archive/daily-log-<year>.md
  - Rows in applications/PIPELINE.md that are Rejected, Withdrawn or No reply,
    with a last contact (or applied date) more than --days ago, go to
    applications/_archive/PIPELINE-ARCHIVE.md

Company folders are left where they are. So is any section of the daily log
whose heading is not a date. Needs Python 3.8+ and nothing else.
"""

import argparse
import re
import sys
from datetime import date, timedelta

from common import ROOT, is_separator, parse_date, split_cells
from pipeline import CLOSED, normalise_stage

LOG = ROOT / "progress" / "daily-log.md"
LOG_ARCHIVE = ROOT / "progress" / "_archive"
PIPELINE = ROOT / "applications" / "PIPELINE.md"
PIPELINE_ARCHIVE = ROOT / "applications" / "_archive" / "PIPELINE-ARCHIVE.md"

ENTRY = re.compile(r"^## (\d{4}-\d{2}-\d{2})\b")
SECTION = re.compile(r"^## ")


def split_log(text):
    """Return (kept, [(date, entry_text), ...]) for a daily log.

    An entry runs from a "## YYYY-MM-DD" heading to the next "## " heading.
    Everything else, including sections with a heading that is not a date,
    is returned in `kept` and never archived.
    """
    kept, entries, current = [], [], None
    for line in text.splitlines():
        match = ENTRY.match(line)
        when = parse_date(match.group(1)) if match else None
        if when:
            current = [when, [line]]
            entries.append(current)
        elif SECTION.match(line):  # a non-dated section ends the entry above it
            if current:
                kept.append("")
            current = None
            kept.append(line)
        elif current:
            current[1].append(line)
        else:
            kept.append(line)
    return "\n".join(kept).rstrip(), [(d, "\n".join(body).rstrip()) for d, body in entries]


def archive_log(cutoff, apply):
    if not LOG.exists():
        return ["progress/daily-log.md not found, skipped"]
    kept, entries = split_log(LOG.read_text(encoding="utf-8"))
    old = [(d, body) for d, body in entries if d < cutoff]
    recent = [(d, body) for d, body in entries if d >= cutoff]
    report = [f"Daily log: {len(old)} of {len(entries)} entries dated before {cutoff}"]
    if not old:
        return report
    by_year = {}
    for when, body in old:
        by_year.setdefault(when.year, []).append((when, body))
    for year, moved in sorted(by_year.items()):
        target = LOG_ARCHIVE / f"daily-log-{year}.md"
        report.append(f"  {len(moved)} -> {target.relative_to(ROOT).as_posix()} "
                      f"({min(d for d, _ in moved)} to {max(d for d, _ in moved)})")
        if apply:
            existing = split_log(target.read_text(encoding="utf-8"))[1] if target.exists() else []
            merged = sorted(existing + moved, key=lambda e: e[0], reverse=True)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f"# Daily Log Archive {year}\n\n"
                              + "\n\n".join(body for _, body in merged) + "\n", encoding="utf-8")
    if apply:
        LOG.write_text("\n\n".join([kept] + [body for _, body in recent]) + "\n", encoding="utf-8")
    return report


def archive_pipeline(cutoff, apply):
    if not PIPELINE.exists():
        return ["applications/PIPELINE.md not found, skipped"]
    header, header_lines, moved, kept, undated, in_table = None, [], [], [], [], False
    for line in PIPELINE.read_text(encoding="utf-8").splitlines():
        is_row = line.strip().startswith("|")
        cells = split_cells(line) if is_row else []
        if header is None and is_row and cells[0].lower() == "company":
            header = [c.lower() for c in cells]
            header_lines.append(line)
            in_table = True
        elif in_table and is_row:
            row = dict(zip(header, cells))
            if is_separator(cells):
                if len(header_lines) == 1 and any(cells):
                    header_lines.append(line)  # the |---| line, kept for the archive file
            elif normalise_stage(row.get("stage", "")) in CLOSED:
                last = parse_date(row.get("last contact", "")) or parse_date(row.get("applied", ""))
                if last and last < cutoff:
                    moved.append(line)
                    continue
                if not last:
                    undated.append(row.get("company", "?"))
        elif in_table:
            in_table = False
        kept.append(line)

    if header is None:
        return ["Pipeline: no table found, skipped"]
    report = [f"Pipeline: {len(moved)} closed application(s) last touched before {cutoff}"]
    for line in moved:
        cells = split_cells(line)
        report.append(f"  {cells[0]} ({cells[2] if len(cells) > 2 else '?'})")
    if moved:
        report.append(f"  -> {PIPELINE_ARCHIVE.relative_to(ROOT).as_posix()}")
    for company in undated:
        report.append(f"  left in place, closed but has no YYYY-MM-DD date: {company}")
    if apply and moved:
        PIPELINE_ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
        if PIPELINE_ARCHIVE.exists():
            archived = PIPELINE_ARCHIVE.read_text(encoding="utf-8").rstrip("\n").splitlines()
        else:
            archived = ["# Pipeline Archive", "",
                        "Closed applications moved out of `applications/PIPELINE.md`. Oldest first.",
                        ""] + header_lines
        PIPELINE_ARCHIVE.write_text("\n".join(archived + moved) + "\n", encoding="utf-8")
        PIPELINE.write_text("\n".join(kept) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description="Archive old log entries and closed applications.")
    parser.add_argument("--days", type=int, default=30, help="keep anything newer than this (default: 30)")
    parser.add_argument("--apply", action="store_true", help="move the items (default is a dry run)")
    args = parser.parse_args()
    if args.days < 1:
        sys.exit("--days must be 1 or more")

    cutoff = date.today() - timedelta(days=args.days)
    for line in archive_log(cutoff, args.apply) + archive_pipeline(cutoff, args.apply):
        print(line)
    print("\nDone." if args.apply else "\nDry run, nothing changed. Add --apply to move these.")


if __name__ == "__main__":
    main()
