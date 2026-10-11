"""Helpers shared by the scripts in this folder. This file is not a command."""

import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Markers the templates ship with. Scripts use them to tell an untouched file from a real one.
RESUME_PLACEHOLDER = "Empty on purpose"  # profile/resume.md before setup has run
UNFILLED = "[fill in]"                   # a template field the user has not completed


def parse_date(text):
    """A YYYY-MM-DD string as a date, or None."""
    try:
        return datetime.strptime(text.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def slug(text):
    """Lower-case with dashes, for comparing a company name with its folder name."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def split_cells(line):
    """Split a Markdown table row on | but not on an escaped \\| inside a cell."""
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


def is_separator(cells):
    """True for the |---|---| line under a header, and for a row with every cell blank."""
    return all(set(c) <= set("-: ") for c in cells)


def read_table(text, first_column=None):
    """Return (header, rows) for the first Markdown table in text.

    With first_column, skip tables whose first header cell is something else.
    header is lower-cased; rows are lists of cells, without separator or blank rows.
    Returns (None, []) when no table matches.
    """
    header, rows = None, []
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            if header:
                break
            continue
        cells = split_cells(line)
        if header is None:
            if first_column is None or cells[0].lower() == first_column:
                header = [c.lower() for c in cells]
        elif not is_separator(cells):
            rows.append(cells)
    return header, rows
