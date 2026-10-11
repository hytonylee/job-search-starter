# Mode: role resume: [role]

Purpose: Build the resume version for one target role.

Reads: `profile/roles.md`, `profile/resume.md`, `profile/profile.md`.

Build the resume version for one target role, so applications for that role start from a closer base.

1. Check the role is in `profile/roles.md`. If not, ask whether to add it.
2. Write `profile/resumes/[role-in-lowercase-with-dashes].md` from `profile/resume.md`: same facts, with the summary, the order of bullets and the skills line arranged for this role. Keep the first heading as my name.
3. Show me what you moved up, what you moved down, and what you left out.
4. Run `python3 scripts/resume.py --role [file name without .md]` and give me the PDF path.

## Rules

- A version only selects, reorders and rewords. Every claim must already be in `profile/resume.md` and backed by `profile/profile.md`.
- If a fact is wrong, fix it in `profile/resume.md` first, then rebuild every version.
- Do not create a version for a role I have not applied to at least once, unless I ask. The master resume is enough to start.
