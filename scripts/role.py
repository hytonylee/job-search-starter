#!/usr/bin/env python3
"""Choose the role this repo is set up for.

Usage:
  python3 scripts/role.py                 list the roles and show the current one
  python3 scripts/role.py product         switch to the product role pack
  python3 scripts/role.py product --force switch even if you edited the files it replaces

A role pack is a folder in roles/ with three files. Switching copies them to
profile/profile.md, modes/practice.md and applications/SCREENING-RUBRIC.md.
Files you have edited are backed up to output/role-backup/ first.
To add a role, copy a folder in roles/ and edit its three files.
"""

import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROLES = ROOT / "roles"
BACKUP = ROOT / "output" / "role-backup"
TARGETS = {
    "profile.md": ROOT / "profile" / "profile.md",
    "practice.md": ROOT / "modes" / "practice.md",
    "rubric.md": ROOT / "applications" / "SCREENING-RUBRIC.md",
}
MARK = re.compile(r"<!--\s*role:\s*([\w-]+)\s*\|\s*(.*?)\s*-->")


def list_roles():
    """Return [(id, label)] for every complete pack in roles/."""
    roles = []
    for folder in sorted(p for p in ROLES.glob("*") if p.is_dir()):
        if all((folder / name).exists() for name in TARGETS):
            mark = MARK.search((folder / "profile.md").read_text(encoding="utf-8"))
            roles.append((folder.name, mark.group(2) if mark else folder.name))
    return roles


def current_role():
    """The role id recorded at the top of profile/profile.md, or None."""
    target = TARGETS["profile.md"]
    if not target.exists():
        return None
    mark = MARK.search(target.read_text(encoding="utf-8"))
    return mark.group(1) if mark else None


def edited_files():
    """Targets that no longer match any pack, meaning the user has changed them."""
    edited = []
    for name, target in TARGETS.items():
        if not target.exists():
            continue
        text = target.read_text(encoding="utf-8")
        originals = [(ROLES / role / name).read_text(encoding="utf-8") for role, _ in list_roles()]
        if text not in originals:
            edited.append(str(target.relative_to(ROOT)))
    return edited


def apply_role(role_id, force=False):
    """Copy a pack into place. Returns a dict describing what happened."""
    if role_id not in [r for r, _ in list_roles()]:
        raise ValueError(f"Unknown role '{role_id}'. Available: " + ", ".join(r for r, _ in list_roles()))
    edited = edited_files()
    if edited and not force:
        return {"applied": False, "edited": edited}
    backup = None
    if edited:
        backup = BACKUP / datetime.now().strftime("%Y-%m-%d-%H%M%S")
        for relative in edited:
            destination = backup / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)
    for name, target in TARGETS.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROLES / role_id / name, target)
    return {"applied": True, "role": role_id, "edited": edited,
            "backup": str(backup.relative_to(ROOT)) if backup else None}


def main():
    parser = argparse.ArgumentParser(description="Choose the role this repo is set up for.")
    parser.add_argument("role", nargs="?", help="role id to switch to (omit to list)")
    parser.add_argument("--force", action="store_true", help="replace files you have edited (they are backed up)")
    args = parser.parse_args()

    if not args.role:
        current = current_role()
        for role_id, label in list_roles():
            print(f"{'*' if role_id == current else ' '} {role_id.ljust(10)} {label}")
        print("\n* current role" if current else "\nNo role recorded in profile/profile.md.")
        return
    try:
        result = apply_role(args.role, args.force)
    except ValueError as error:
        sys.exit(str(error))
    if not result["applied"]:
        print("Not switched. You have edited these files, and switching replaces them:")
        for path in result["edited"]:
            print(f"  {path}")
        print("Run again with --force to back them up and switch.")
        sys.exit(1)
    print(f"Role set to {args.role}.")
    if result["backup"]:
        print(f"Your edited files were backed up to {result['backup']}/")


if __name__ == "__main__":
    main()
