# Mode: setup

The onboarding interview. It sets the project up by asking me questions, one step at a time. Safe to run again: it picks up where it stopped.

## How to run it

- Before each step, check the files to see whether it is already done. Skip finished steps and tell me which you skipped.
- Announce each step as "Step N of 7" with one line on why it matters.
- Ask one question at a time and wait for my answer. Never invent a fact about me. If I do not know, write `[to confirm]`.
- After each step, save the files and tell me the dashboard now shows it. The dashboard updates by itself.
- If I stop partway, add a `progress/daily-log.md` entry naming the next step, so the next session resumes there.

## Steps

1. **Target roles.** Read `profile/roles.md`. If it has no real roles, ask which job titles I am applying for (several is fine) and which is primary. Save them there.
2. **Resume source.** Look for `profile/linkedin-export.pdf`. If it is missing, tell me how to get it (LinkedIn profile → Resources → Save to PDF, saved into `profile/`) and wait. If I have no LinkedIn profile, ask me to paste my current resume as text instead.
3. **Master resume.** Write `profile/resume.md` from that source in clean Markdown, changing no wording yet. Fill `profile/linkedin-profile.md` with the same text section by section and set "Last synced" to today.
4. **The basics.** Ask, one at a time: where I am based and my work authorization; the level I am targeting; my salary floor; remote, hybrid or on-site; anything that makes a job an automatic no. Write the first three to the header of `profile/profile.md` and the rest to the hard stops in `applications/SCREENING-RUBRIC.md`.
5. **Tailor to my roles.** Follow `modes/roles.md` to build the profile table, the practice exercises and the role-specific rubric lines.
6. **Audit.** Follow `modes/audit.md`, starting with my most recent job. After that job, ask whether to continue now or later. Later is fine.
7. **First application.** Ask whether I have a posting ready. If yes, follow `modes/apply.md`. If no, tell me to come back with `apply: [company]`.

## When it ends

Give me a five-line summary: what is set up, what is still open, and the one keyword to type next. Add the `progress/daily-log.md` entry.
