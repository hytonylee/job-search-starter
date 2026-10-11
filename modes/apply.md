# Mode: apply: [company]

Purpose: Check a posting, tailor the resume and track the application.

Reads: `applications/SCREENING-RUBRIC.md`, `profile/roles.md`, `profile/profile.md`. I paste the posting.

1. Save the posting to `applications/[company]/posting.md`.
2. Say which of my target roles this posting matches. If it matches none, say so before going further.
3. Score it against the rubric. Tell me **apply or skip** before writing anything else. If skip, log the unmet required items in `progress/weak-spots.md` and stop.
4. Write `applications/[company]/fit.md`: the matched target role, then each required item, whether I meet it, and the evidence from `profile/profile.md`. Put the fit score on its first line after the title, as required items met out of the number listed, for example `Fit: 4/5`.
5. Draft `applications/[company]/resume.md`. Start from `profile/resumes/[matched role].md` if it exists, otherwise from `profile/resume.md`. Tailor by reordering and rewording verified items only. Never add a skill that is not in `profile/profile.md`.
6. Draft `applications/[company]/cover-note.md` only if the posting asks for one. Under 150 words, written for this company and this role, never reused from another application.
7. When I approve the tailored resume, run `python3 scripts/resume.py [company]` and give me the PDF path.
8. Add a row to `applications/PIPELINE.md` as **Drafted**, with a cell for every column in its header, the same fit score in the Fit column, and Furthest left blank. If the application moves to an interview, remind me to run `research: [company]` first. Change it to **Applied** only when I say I submitted.
9. Add each unmet required item to `progress/weak-spots.md`, or raise its count if it is already there.

Company folder layout is described in `applications/_example-company/README.md`.
