# Job Search Starter

A folder of plain text files that turns an AI coding tool (Codex, Cursor, Claude Code) into a job-search coach that remembers your history. The AI reads `AGENTS.md` at the start of every session, so it knows who you are, where every application stands, and which gaps real postings have exposed.

## Where this came from

I built the original version of this for my own job search as a product engineer, and kept changing it as I learned what worked. This repo is the reusable part of that setup with everything personal removed.

Right now it is configured for a friend looking for a **DevOps** position. The method works for other roles, but a few files assume DevOps. If you want to use it, follow the instructions below and **change the target role first** so it suits you. See [Change it to your role](#change-it-to-your-role).

## How it works

Everything serves one loop:

1. **Seed.** Your LinkedIn profile export becomes `resume.md`.
2. **Audit.** Every resume line gets evidence or gets cut.
3. **Apply.** Each real posting gets a folder and a row in the pipeline.
4. **Collect gaps.** Every posting and interview adds evidence to a ranked gap list.
5. **Plan the day.** From the pipeline and the gap list, not from mood.
6. **Sync LinkedIn.** The resume is the source and the profile is a copy.

## Setup, about 10 minutes

1. Click **Use this template** on GitHub and create your own copy. **Make it private.** It will hold your resume, salary floor and interview notes. Do not work in a fork or a clone of this repo.
2. Clone your copy to your machine.
3. On LinkedIn, open your profile, then **Resources → Save to PDF**. Save the file in the folder as `linkedin-export.pdf`.
4. Open the folder in your tool:
   - **Codex:** run `codex` inside the folder. It reads `AGENTS.md` automatically.
   - **Cursor:** open the folder and use Agent mode. It reads `AGENTS.md` automatically.
   - **Claude Code:** run `claude` inside the folder. Create a `CLAUDE.md` containing the single line `@AGENTS.md`.
5. If you are not looking for a DevOps role, do [Change it to your role](#change-it-to-your-role) now.
6. Type `setup`.

## Change it to your role

Six places mention DevOps. Edit them by hand, or ask your AI tool: "Adapt this repo for a [your role] job search. Change only the role-specific parts listed in the README."

| File | What to change |
|---|---|
| `AGENTS.md` | The first line says "senior DevOps interviewer." Put your target role's interviewer |
| `profile.md` | The experience table rows (cloud, IaC, containers...). Use the skill areas of your role |
| `modes/troubleshoot.md` | Broken-system scenarios. Replace with your role's live exercise: a coding task, a product case, a portfolio critique, a mock sales call |
| `modes/gaps.md` | "A rep means build or break something." Replace with producing your role's real work: a feature, a PRD, a campaign brief |
| `modes/mock-interview.md` | Step 3 points to the troubleshooting scenario. Point it at your replacement |
| `applications/SCREENING-RUBRIC.md` | The on-call hard stop and the DevOps warning sign. Use your role's equivalents |

Everything else is role-neutral.

## First session, 60 to 90 minutes

1. `setup` turns the LinkedIn export into `resume.md`.
2. `audit` walks every line and asks for evidence. Expect it to cut things. That is the point.
3. Fill in `applications/SCREENING-RUBRIC.md` with your own must-haves.
4. `apply: [company]` on one real posting, start to finish.

## Every day after

- `check in` to plan the day.
- `apply: [company]` for each posting.
- `debrief: [company]` within an hour of any call, while you still remember the questions.
- One gap rep from `progress/weak-spots.md`.
- `linkedin sync` whenever `resume.md` changes.

All keywords are listed in `AGENTS.md`.

## Three things that make it work

1. **Keep everything in this folder.** A browser chat cannot see these files, so it fills the holes with confident guesses.
2. **Add rules as you learn, in the right file.** When you notice a pattern in how you fail (rambling, vague answers, skipping follow-ups), write it into the mode file where it applies, such as `modes/drill.md`. The rules that help most are the ones you add yourself.
3. **Let postings choose what you study.** After 5 to 10 applications the same missing skill will show up again and again. Study that, not a roadmap.

## Keeping it cheap to run

`AGENTS.md` is loaded into every session, so it stays a short index. Each keyword has its own file in `modes/`, which the AI opens only when you type that keyword. Keep it that way: new detail goes in a mode file, `profile.md` or `notes/`, never in `AGENTS.md`. Start a fresh session for each task instead of running one long one.

## Limitations

- **It comes from one person's search.** The rules reflect what one product engineer needed. Some will not fit you, and your own failure patterns are not in here yet.
- **This cleaned-up version is new.** The method was used for a real search in Claude Code. This template has not yet been run end to end in Codex or Cursor.
- **Mode files rely on the AI following a pointer.** If a keyword runs without its rules, tell the tool directly: "follow `modes/apply.md`."
- **It does not find jobs.** You bring the postings. There is no job-board search, scraping or auto-apply.
- **Nothing is automated.** The pipeline is a Markdown table the AI edits, LinkedIn is updated by hand, and there are no reminders. If you skip `check in`, nothing nudges you.
- **No resume export.** `resume.md` is Markdown. Turning it into a PDF is up to you.
- **Memory is manual.** Codex and Cursor do not carry memory between sessions, so anything worth keeping has to be written to `notes/`.
- **The audit is only as honest as you are.** The AI cannot check your claims against anything except what you tell it.
- **The AI can still be wrong.** It can misread a posting or score an answer too kindly. Treat scores as a prompt to think, not a verdict.
- **Files grow.** `daily-log.md` and `PIPELINE.md` get long over months and cost more to read. Move old entries to an archive file now and then.
- **Your data goes to your AI provider.** Whatever the tool reads is sent to that provider under its terms. Check them before adding anything sensitive.
- **It needs some comfort with a code editor or terminal.** A non-technical user will want someone beside them for the first session.

## Ideas for improvement

- **Role packs.** Ready-made `profile.md`, practice mode and rubric for other roles (frontend, backend, product, design, data) so no hand-editing is needed.
- **A pipeline script.** A small script that prints the pipeline as a summary, flags overdue follow-ups and computes the weekly numbers.
- **Resume export.** A one-command Markdown to PDF build with a clean template.
- **Native commands per tool.** Slash commands for Cursor and Codex that wrap each mode, so the right file is always loaded.
- **Log archiving.** A mode that rolls old log entries and closed applications into archive files.
- **More modes.** Offer review and negotiation, networking and referral tracking, recruiter reply drafting, a weekly review.
- **A worked example.** A fictional candidate carried through the whole loop, so a new user can see what filled-in files look like.
- **Tested notes per tool.** What actually happens in Codex and Cursor, once someone has run it there.

If you improve it, a pull request to the template is welcome. Keep your personal files out of it.

## Questions

If you have any questions, feel free to ping me on [LinkedIn](https://www.linkedin.com/in/hytonylee). You can also find me at [www.hytonylee.com](https://www.hytonylee.com).

## Do not put in this folder

Secrets, tokens, kubeconfigs, internal hostnames, or anything copied from an employer's systems.
