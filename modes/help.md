# Mode: help

Purpose: List every keyword and script command (`commands` works too).

Also triggered by `commands`. Reads: nothing.

1. Run `python3 scripts/commands.py`.
2. Show me the output as is. Do not add to it or explain it unless I ask.

If Python is not available, print the keyword list from `AGENTS.md` and the usage lines at the top of each file in `scripts/`.

The list is built from three places, so keep them in step: the keyword list in `AGENTS.md`, the `Purpose:` line at the top of each file in `modes/`, and the Usage block at the top of each script, including every flag. A keyword's file is named after it, with dashes for spaces. A script with no Usage block is treated as a helper and not listed.
