#!/usr/bin/env python3
"""List every keyword and script command in this repo.

Usage:
  python3 scripts/commands.py    print keywords and script commands

Keywords come from the list in AGENTS.md, each with the "Purpose:" line of its
file in modes/. Script commands come from each script's own usage text. A
script without a Usage block is a helper, not a command, and is left out.
"""

import ast
import re
import sys

from common import ROOT

AGENTS = ROOT / "AGENTS.md"
MODES = ROOT / "modes"
SCRIPTS = ROOT / "scripts"


def mode_file(keyword):
    """modes/check-in.md for "check in"; modes/apply.md for "apply: [company]"."""
    return MODES / (keyword.split(":")[0].strip().replace(" ", "-") + ".md")


def keywords():
    """Every keyword as (keyword, purpose), in the order AGENTS.md lists them."""
    section = re.search(r"^## Keywords\n(.*?)(?=^## |\Z)", AGENTS.read_text(encoding="utf-8", errors="replace"), flags=re.M | re.S)
    listed = [line for line in (section.group(1) if section else "").splitlines() if " · " in line]
    rows = []
    for keyword in re.findall(r"`([^`]+)`", listed[0] if listed else ""):
        path = mode_file(keyword)
        purpose = ""
        if path.exists():
            found = re.search(r"^Purpose:\s*(.+?)\.?$", path.read_text(encoding="utf-8", errors="replace"), flags=re.M)
            purpose = found.group(1) if found else ""
        rows.append((keyword, purpose or "(no mode file found)"))
    return rows


def script_usage(path):
    """Return (summary, [(command, what it does), ...]) from a script's docstring."""
    doc = ast.get_docstring(ast.parse(path.read_text(encoding="utf-8", errors="replace"))) or ""
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
