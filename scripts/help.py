#!/usr/bin/env python3
"""List every keyword and script command in this repo.

Usage:
  python3 scripts/help.py    print keywords and script commands

Keywords are read from the table in AGENTS.md and script commands from each
script's own usage text, so this list cannot drift from the real thing.
"""

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS = ROOT / "AGENTS.md"
SCRIPTS = ROOT / "scripts"


def keywords():
    """Rows of the Modes table: (keyword, purpose)."""
    rows = []
    for line in AGENTS.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
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


def main():
    if not AGENTS.exists():
        sys.exit("AGENTS.md not found")
    rows = keywords()
    width = max(len(k) for k, _ in rows) if rows else 0
    print("KEYWORDS  (type these to your AI tool)\n")
    for keyword, purpose in rows:
        print(f"  {keyword.ljust(width)}  {purpose}")

    print("\nSCRIPTS  (run these in a terminal, from the repo folder)")
    for path in sorted(SCRIPTS.glob("*.py")):
        summary, commands = script_usage(path)
        print(f"\n  {path.name}: {summary}")
        width = max((len(c) for c, _ in commands), default=0)
        for command, about in commands:
            print(f"    {command.ljust(width)}  {about}".rstrip())

    print("\nEach keyword's full instructions are in modes/. Setup and background are in README.md.")


if __name__ == "__main__":
    main()
