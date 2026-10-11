#!/usr/bin/env python3
"""List every keyword and script command in this repo.

Usage:
  python3 scripts/commands.py    print keywords and script commands

Keywords are read from the table in AGENTS.md and script commands from each
script's own usage text. A script without a Usage block is a helper, not a
command, and is left out.
"""

import ast
import re
import sys

from common import ROOT, split_cells

AGENTS = ROOT / "AGENTS.md"
SCRIPTS = ROOT / "scripts"


def keywords():
    """Rows of the Modes table: (keyword, purpose)."""
    rows = []
    for line in AGENTS.read_text(encoding="utf-8").splitlines():
        cells = split_cells(line)
        if len(cells) == 3 and re.fullmatch(r"`modes/[\w-]+\.md`", cells[1]):
            rows.append((cells[0].strip("`"), cells[2]))
    return rows


def script_usage(path):
    """Return (summary, [(command, what it does), ...]) from a script's docstring."""
    doc = ast.get_docstring(ast.parse(path.read_text(encoding="utf-8"))) or ""
    lines = doc.splitlines()
    summary = lines[0] if lines else ""
    commands, in_usage = [], False
    for line in lines[1:]:
        if line.strip() == "Usage:":
            in_usage = True
        elif in_usage and not line.strip():
            break
        elif in_usage:
            command, _, about = line.strip().partition("  ")
            commands.append((command.strip(), about.strip()))
    return summary, commands


def script_commands():
    """Every runnable script as (file name, summary, commands). Helpers with no Usage block are skipped."""
    found = []
    for path in sorted(SCRIPTS.glob("*.py")):
        summary, commands = script_usage(path)
        if commands:
            found.append((path.name, summary, commands))
    return found


def main():
    if not AGENTS.exists():
        sys.exit("AGENTS.md not found")
    rows = keywords()
    width = max(len(k) for k, _ in rows) if rows else 0
    print("KEYWORDS  (type these to your AI tool)\n")
    for keyword, purpose in rows:
        print(f"  {keyword.ljust(width)}  {purpose}")

    print("\nSCRIPTS  (run these in a terminal, from the repo folder)")
    for name, summary, commands in script_commands():
        print(f"\n  {name}: {summary}")
        width = max(len(c) for c, _ in commands)
        for command, about in commands:
            print(f"    {command.ljust(width)}  {about}".rstrip())

    print("\nEach keyword's full instructions are in modes/. Setup and background are in README.md.")


if __name__ == "__main__":
    main()
