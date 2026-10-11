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
MAX_DAYS = 3650


def split_log(text):
    """The log as blocks in their original order: (date or None, [lines]).

    A block with a date is one entry, running from its "## YYYY-MM-DD" heading
    to the next "## " heading. Every other stretch of the file, including a
    section whose heading is not a date, is a block with date None.
    """
    blocks = [(None, [])]
    for line in text.splitlines():
        match = ENTRY.match(line)
        when = parse_date(match.group(1)) if match else None
        if when or SECTION.match(line):
            blocks.append((when, []))
        blocks[-1][1].append(line)
    return [block for block in blocks if block[1]]


def log_entries(text):
    """The dated entries of a log as (date, text), in file order."""
    return [(when, "\n".join(lines).rstrip()) for when, lines in split_log(text) if when]


def archive_log(cutoff, apply):
    """Returns (report lines, number of entries that move)."""
    if not LOG.exists():
        return ["progress/daily-log.md not found, skipped"], 0
    blocks = split_log(LOG.read_text(encoding="utf-8", errors="replace"))
    entries = [(when, lines) for when, lines in blocks if when]
    old = [(when, "\n".join(lines).rstrip()) for when, lines in entries if when < cutoff]
    report = [f"Daily log: {len(old)} of {len(entries)} entries dated before {cutoff}"]
    if not old:
        return report, 0
    by_year = {}
    for when, body in old:
        by_year.setdefault(when.year, []).append((when, body))
    for year, moved in sorted(by_year.items()):
        target = LOG_ARCHIVE / f"daily-log-{year}.md"
        report.append(f"  {len(moved)} -> {target.relative_to(ROOT).as_posix()} "
                      f"({min(d for d, _ in moved)} to {max(d for d, _ in moved)})")
        if apply:
            existing = log_entries(target.read_text(encoding="utf-8", errors="replace")) if target.exists() else []
            merged = sorted(existing + moved, key=lambda e: e[0], reverse=True)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f"# Daily Log Archive {year}\n\n"
                              + "\n\n".join(body for _, body in merged) + "\n", encoding="utf-8")
    if apply:  # everything that stays keeps its original order and spacing
        kept = [line for when, lines in blocks if not (when and when < cutoff) for line in lines]
        LOG.write_text("\n".join(kept).rstrip() + "\n", encoding="utf-8")
    return report, len(old)


def archive_pipeline(cutoff, apply):
    """Returns (report lines, number of rows that move)."""
    if not PIPELINE.exists():
        return ["applications/PIPELINE.md not found, skipped"], 0
    header, header_lines, moved, kept, undated, in_table = None, [], [], [], [], False
    for line in PIPELINE.read_text(encoding="utf-8", errors="replace").splitlines():
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
        return ["Pipeline: no table found, skipped"], 0
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
    return report, len(moved)


def run(days, apply):
    """Archive both files. Returns {"days", "applied", "report", "moved"}; a dry run unless apply."""
    days = max(1, min(int(days), MAX_DAYS))
    cutoff = date.today() - timedelta(days=days)
    log_report, log_count = archive_log(cutoff, apply)
    row_report, row_count = archive_pipeline(cutoff, apply)
    return {"days": days, "applied": bool(apply), "report": log_report + row_report, "moved": log_count + row_count}


def main():
    parser = argparse.ArgumentParser(description="Archive old log entries and closed applications.")
    parser.add_argument("--days", type=int, default=30, help="keep anything newer than this (default: 30)")
    parser.add_argument("--apply", action="store_true", help="move the items (default is a dry run)")
    args = parser.parse_args()
    if not 1 <= args.days <= MAX_DAYS:
        sys.exit(f"--days must be between 1 and {MAX_DAYS}")

    result = run(args.days, args.apply)
    for line in result["report"]:
        print(line)
    if not result["moved"]:
        print("\nNothing to archive.")
    else:
        print("\nDone." if args.apply else "\nDry run, nothing changed. Add --apply to move these.")


if __name__ == "__main__":
    main()
