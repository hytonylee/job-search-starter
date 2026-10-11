# Job Search Starter

A folder of plain text files that turns an AI coding tool (Codex, Cursor, Claude Code) into a job-search coach that remembers your history. The AI reads `AGENTS.md` at the start of every session, so it knows who you are, where every application stands, and which gaps real postings have exposed.

## Where this came from

I built the original version of this for my own job search as a product engineer, and kept changing it as I learned what worked. This repo is the reusable part of that setup with everything personal removed.

Right now it is configured for a friend looking for a **DevOps** position, and it ships with role packs for frontend, backend, product, design and data as well. If you want to use it, follow the instructions below and **choose your role first** so it suits you. See [Choose your role](#choose-your-role).

## How it works

Everything serves one loop:

1. **Seed.** Your LinkedIn profile export becomes `profile/resume.md`.
2. **Audit.** Every resume line gets evidence or gets cut.
3. **Apply.** Each real posting gets a folder and a row in the pipeline.
4. **Collect gaps.** Every posting and interview adds evidence to a ranked gap list.
5. **Plan the day.** From the pipeline and the gap list, not from mood.
6. **Sync LinkedIn.** The resume is the source and the profile is a copy.

## What is in the repo

```
AGENTS.md            the index the AI reads every session
README.md            this file
profile/             who you are: profile, resume, LinkedIn text and export
modes/               one instruction file per keyword
applications/        the pipeline, the screening rubric, one folder per company
progress/            daily log and the ranked gap list
notes/               long-term memory, one fact per file
roles/               ready-made role packs: devops, frontend, backend, product, design, data
scripts/             dashboard, pipeline viewer, resume export, archiving, role picker, help
ui/                  the dashboard page
output/              generated files: pipeline page, exported resumes (not committed)
```

Only `AGENTS.md` and `README.md` sit at the top level. Source files live in their folders, and anything a script generates goes to `output/`. Old entries move to `_archive/` folders inside `progress/` and `applications/`.

## Setup, about 10 minutes

1. Click **Use this template** on GitHub and create your own copy. **Make it private.** It will hold your resume, salary floor and interview notes. Do not work in a fork or a clone of this repo.
2. Clone your copy to your machine.
3. On LinkedIn, open your profile, then **Resources → Save to PDF**. Save the file in the folder as `profile/linkedin-export.pdf`.
4. Open the folder in your tool:
   - **Codex:** run `codex` inside the folder. It reads `AGENTS.md` automatically.
   - **Cursor:** open the folder and use Agent mode. It reads `AGENTS.md` automatically.
   - **Claude Code:** run `claude` inside the folder. Create a `CLAUDE.md` containing the single line `@AGENTS.md`.
5. Start the dashboard with `python3 scripts/app.py` and [choose your role](#choose-your-role) on the Start tab.
6. Type `setup` in your AI tool.

## The dashboard

A local web page for reading your material, so you are not limited to the terminal.

```bash
python3 scripts/app.py
```

It opens in your browser. It runs only on your own computer, sends nothing anywhere, and stops when you press Ctrl+C.

| Tab | What you see |
|---|---|
| **Start** | The role picker and a setup checklist that ticks itself off |
| **Pipeline** | Counts per stage, what needs attention, every application |
| **Applications** | One company at a time: the posting, your fit, the tailored resume, interview notes, and a PDF export button |
| **Prep** | Your profile, resume, gap list, practice exercise and every interview question you have logged, formatted for reading before an interview |
| **Progress** | Applications sent, interviews reached, practice scores over time, and recent sessions |
| **Tools** | Resume export, archiving with a preview, and every keyword with a copy button |

The page reads your files and shows them. The coaching itself still happens in your AI tool: you type a keyword there, it updates the files, and you press **Refresh** here. To change a document, edit the file or ask the AI.

## Choose your role

Six role packs are included: **devops** (the default), **frontend**, **backend**, **product**, **design** and **data**. Pick one on the dashboard's Start tab, or in the terminal:

```bash
python3 scripts/role.py            # list roles and show the current one
python3 scripts/role.py product    # switch
```

Choosing a role replaces three files: the experience table in `profile/profile.md`, the live exercise in `modes/practice.md`, and `applications/SCREENING-RUBRIC.md`. The exercise differs by role: a troubleshooting scenario for DevOps, live coding for frontend, a product case for product, a portfolio walkthrough for design, a SQL case for data. Everything else is role-neutral.

Choose before you fill anything in. If you switch later, any of the three files you have edited is backed up to `output/role-backup/` first, and you will need to redo your profile.

**Your role is not listed?** Copy a folder in `roles/`, rename it, and edit its three files. It appears in the picker straight away.

## First session, 60 to 90 minutes

1. `setup` turns the LinkedIn export into `profile/resume.md`.
2. `audit` walks every line and asks for evidence. Expect it to cut things. That is the point.
3. Fill in `applications/SCREENING-RUBRIC.md` with your own must-haves.
4. `apply: [company]` on one real posting, start to finish.

## Every day after

- `check in` to plan the day.
- `apply: [company]` for each posting.
- `debrief: [company]` within an hour of any call, while you still remember the questions.
- One gap rep from `progress/weak-spots.md`.
- `linkedin sync` whenever `profile/resume.md` changes.

## List every command

Type `help` (or `commands`) in your AI tool, or run:

```bash
python3 scripts/help.py
```

It prints every keyword and every script command. The list is built from the table in `AGENTS.md` and each script's own usage text, so it stays current when you add your own. The word is `help`, not `/help`, because `/help` is already a built-in command in most of these tools.

The scripts need Python 3.8 or newer and nothing else to install.

## See your pipeline

Type `pipeline` in your AI tool, or run the script yourself.

```bash
python3 scripts/pipeline.py           # table in the terminal
python3 scripts/pipeline.py --html    # also writes output/pipeline.html
python3 scripts/pipeline.py --open    # writes the page and opens it in your browser
```

It shows every application with its stage, a count per stage, and flags two things: a next action whose due date has passed, and an application with no contact for 21 days. It reads `applications/PIPELINE.md`, so keep that table's column names and use `YYYY-MM-DD` dates.

## Export your resume

Type `export resume` or `export resume: [company]`, or run:

```bash
python3 scripts/resume.py              # the base resume, profile/resume.md
python3 scripts/resume.py acme         # the tailored one, applications/acme/resume.md
python3 scripts/resume.py acme --open  # export, then open it
python3 scripts/resume.py --paper a4   # A4 instead of US Letter
```

Each run writes three files to `output/resume/general/` or `output/resume/<company>/`: a clean `.md`, an `.html`, and a `.pdf`. They are named after the first heading in the resume, for example `Jane-Doe-Resume.pdf`.

The PDF is printed by a Chromium-based browser you already have (Chrome, Chromium, Edge or Brave). If none is found, open the `.html` file in any browser and use Print, then Save as PDF. The layout is a plain single column with real text, which is what applicant tracking systems read best. Always open the PDF and check it before sending.

## Archive old entries

Type `archive` about once a month, or run:

```bash
python3 scripts/archive.py            # dry run: shows what would move
python3 scripts/archive.py --apply    # moves it
python3 scripts/archive.py --days 14  # 14 day cut-off instead of 30
```

Daily-log entries older than the cut-off move to `progress/_archive/daily-log-<year>.md`. Pipeline rows that are Rejected, Withdrawn or No reply and were last touched before the cut-off move to `applications/_archive/PIPELINE-ARCHIVE.md`. Company folders stay where they are. This keeps the files the AI reads every day short.

## Three things that make it work

1. **Keep everything in this folder.** A browser chat cannot see these files, so it fills the holes with confident guesses.
2. **Add rules as you learn, in the right file.** When you notice a pattern in how you fail (rambling, vague answers, skipping follow-ups), write it into the mode file where it applies, such as `modes/drill.md`. The rules that help most are the ones you add yourself.
3. **Let postings choose what you study.** After 5 to 10 applications the same missing skill will show up again and again. Study that, not a roadmap.

## Keeping it cheap to run

`AGENTS.md` is loaded into every session, so it stays a short index. Each keyword has its own file in `modes/`, which the AI opens only when you type that keyword. Keep it that way: new detail goes in a mode file, `profile/profile.md` or `notes/`, never in `AGENTS.md`. Start a fresh session for each task instead of running one long one.

## Limitations

- **It comes from one person's search.** The rules reflect what one product engineer needed. Some will not fit you, and your own failure patterns are not in here yet.
- **This cleaned-up version is new.** The method was used for a real search in Claude Code. This template has not yet been run end to end in Codex or Cursor.
- **Mode files rely on the AI following a pointer.** If a keyword runs without its rules, tell the tool directly: "follow `modes/apply.md`."
- **It does not find jobs.** You bring the postings. There is no job-board search, scraping or auto-apply.
- **Very little is automated.** The pipeline is a Markdown table the AI edits, and the script only displays it. LinkedIn is updated by hand, and there are no reminders. If you skip `check in`, nothing nudges you.
- **The pipeline script is strict about format.** It lists rows with an unknown stage, a date that is not `YYYY-MM-DD`, or missing columns, but it cannot flag a follow-up on those rows until you fix them. Renaming a column breaks it.
- **Only two things are flagged.** An overdue next action, and an application in the Applied stage with no contact for 21 days. Silence after an interview is not flagged unless you set a due date.
- **Resume export is basic.** One fixed single-column layout. It handles headings, paragraphs, bullets, bold, italic and links, but not tables, images or columns. The PDF needs a Chromium-based browser, and nothing checks the page count for you.
- **Memory is manual.** Codex and Cursor do not carry memory between sessions, so anything worth keeping has to be written to `notes/`.
- **The audit is only as honest as you are.** The AI cannot check your claims against anything except what you tell it.
- **The AI can still be wrong.** It can misread a posting or score an answer too kindly. Treat scores as a prompt to think, not a verdict.
- **Archiving is manual and by date only.** Nothing reminds you to run it. It skips a closed application with no valid date, and it never moves company folders or old notes.
- **Your data goes to your AI provider.** Whatever the tool reads is sent to that provider under its terms. Check them before adding anything sensitive.
- **You still need a terminal once or twice.** The dashboard is started from one, and the AI tool is opened on the folder. A non-technical user will want someone beside them for the first session.
- **The dashboard is for reading.** Apart from the role picker, resume export and archiving, it changes nothing. You cannot edit a document, add an application or run a coaching session from it.
- **The dashboard and role packs are new.** The page logic was tested with sample data but has had little real use. The five non-DevOps role packs were written from general knowledge of those interviews, not from a real search in each role, so expect to adjust them.
- **Progress numbers depend on the AI logging them.** Practice scores appear only if the AI adds the row to `progress/practice-log.md` at the end of a session.

## Ideas for improvement

- **More role packs.** Product marketing, UX research, engineering management, QA, customer success, sales. Better still, packs reviewed by someone who hires for that role.
- **Editing from the dashboard.** Update a pipeline row, tick a rubric item or add a note without opening a file.
- **A richer pipeline view.** Compute the weekly numbers and reply rate automatically, flag silence after interviews, and chart applications over time.
- **Resume templates.** A choice of layouts, a page-count warning, and a `.docx` export for employers that ask for Word.
- **Native commands per tool.** Slash commands for Cursor and Codex that wrap each mode, so the right file is always loaded.
- **More modes.** Offer review and negotiation, networking and referral tracking, recruiter reply drafting, a weekly review.
- **A worked example.** A fictional candidate carried through the whole loop, so a new user can see what filled-in files look like.
- **Tested notes per tool.** What actually happens in Codex and Cursor, once someone has run it there.

If you improve it, a pull request to the template is welcome. Keep your personal files out of it.

## Questions

If you have any questions, feel free to ping me on [LinkedIn](https://www.linkedin.com/in/hytonylee). You can also find me at [www.hytonylee.com](https://www.hytonylee.com).

## Do not put in this folder

Secrets, tokens, kubeconfigs, internal hostnames, or anything copied from an employer's systems.
