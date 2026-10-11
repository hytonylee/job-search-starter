# Job Search Starter

A folder of plain text files that turns an AI coding tool (Codex, Cursor, Claude Code) into a job-search coach that remembers your history. The AI reads `AGENTS.md` at the start of every session, so it knows who you are, where every application stands, and which gaps real postings have exposed.

## Where this came from

I built the original version of this for my own job search as a product engineer, and kept changing it as I learned what worked. This repo is the reusable part of that setup with everything personal removed.

It began as a setup for a friend looking for a DevOps position and now works for any role, or several at once. You tell it the job titles you are targeting, in your own words, and it shapes itself around them. See [Your target roles](#your-target-roles).

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
profile/             who you are: target roles, profile, master resume, a resume version per role, interview stories, LinkedIn text
modes/               one instruction file per keyword
applications/        the pipeline, the screening rubric, one folder per company
progress/            daily log and the ranked gap list
notes/               long-term memory, one fact per file
roles/               example patterns the AI adapts to your roles (devops, frontend, backend, product, design, data)
scripts/             dashboard, pipeline viewer, resume export, story coverage, archiving, help
ui/                  the dashboard page
start/               double-click launchers for the dashboard (Mac and Windows)
example/             a fictional candidate for the dashboard's "See an example" view
output/              generated files: pipeline page, exported resumes (not committed)
```

Only `AGENTS.md` and `README.md` sit at the top level, apart from git's own dotfiles and, if you use Claude Code, a one-line `CLAUDE.md` pointer. Source files live in their folders, and anything a script generates goes to `output/`. Old entries move to `_archive/` folders inside `progress/` and `applications/`.

## Setup, about 10 minutes

1. Click **Use this template** on GitHub and create your own copy. **Make it private.** It will hold your resume, salary floor and interview notes. Do not work in a fork or a clone of this repo.
2. Clone your copy to your machine.
3. On LinkedIn, open your profile, then **Resources → Save to PDF**. Save the file in the folder as `profile/linkedin-export.pdf`.
4. Open the folder in your tool:
   - **Codex:** run `codex` inside the folder. It reads `AGENTS.md` automatically.
   - **Cursor:** open the folder and use Agent mode. It reads `AGENTS.md` automatically.
   - **Claude Code:** run `claude` inside the folder. Create a `CLAUDE.md` containing the single line `@AGENTS.md`.
5. Open [the dashboard](#the-dashboard) and press **Start project onboarding**. It gives you a first message to paste into your AI tool.
6. Paste it. The AI asks you a series of questions and sets the project up step by step.

## The dashboard

A local web page for reading your material, so you are not limited to the terminal.

**To open it, double-click the launcher in the `start/` folder:**

| Your computer | Double-click |
|---|---|
| Mac | `start/dashboard-mac.command` |
| Windows | `start/dashboard-windows.bat` |

A small window opens and stays open while the dashboard runs, and the page appears in your browser at `http://127.0.0.1:8765/`. To stop it, close that window. If you double-click again while it is running, it opens the one already running instead of starting a second. If that port is taken by another program, it uses the next free one and says which. On Linux, or if you prefer a terminal, run `python3 scripts/app.py` from the repo folder.

It runs only on your own computer and sends nothing anywhere. That also means the address works only on your machine: it is not a link you can send to someone else.

If the launcher does not start:

- **"Python 3 is not installed."** Install it from [python.org/downloads](https://www.python.org/downloads/). On Windows, tick "Add python.exe to PATH" during the install. On a Mac the message reads "Python 3 is not ready", and macOS may offer to install Apple's developer tools, which include Python: accept, wait for it to finish, and double-click again.
- **Mac says the file cannot be opened, or is from an unidentified developer.** This happens if you downloaded the repo as a ZIP instead of cloning it. Right-click the file, choose Open, then Open again. You only need to do this once.
- **Mac says you do not have permission.** In Terminal, run `chmod +x start/dashboard-mac.command` from the repo folder.
- **Windows shows "Windows protected your PC".** Click More info, then Run anyway.

| Tab | What you see |
|---|---|
| **Start** | The onboarding button (it shows where this folder is on your computer, how to open it in your AI tool, and the first message to paste), your target roles, and a setup checklist that ticks itself off |
| **Pipeline** | Counts per stage, what needs attention, every application |
| **Applications** | One company at a time: the posting, your fit, the tailored resume, interview notes, and a PDF export button |
| **Prep** | Your profile, master resume and role versions, interview stories with their coverage, gap list, practice exercises and every interview question you have logged, formatted for reading before an interview |
| **Progress** | Applications sent, interviews reached, offers, questions with a story, practice scores over time, and recent sessions. Totals include archived applications, and an interview counts once interview notes exist for that company |
| **Tools** | Export of the master resume or a role version, archiving with a preview, and every keyword with a copy button |

**See an example.** A new project is empty, so the dashboard has a **See an example** button. It switches every tab to a fictional candidate, Sam Rivera, seven weeks into a product management search: a pipeline with follow-ups due, tailored applications, company research, STAR stories and practice scores. It is read-only and kept in its own `example/` folder, so it never mixes with your files and your AI tool never reads it. Press **Back to my data** to return. You can delete the folder, and the button goes with it.

The page reads your files and shows them. The coaching itself still happens in your AI tool: you type a keyword there, it updates the files, and the page picks up the change within a few seconds, or as soon as you switch back to it. It holds off while you are typing, have unsaved roles, or have an archive preview open, and says so next to the **Refresh** button. To change a document, edit the file or ask the AI.

## Your target roles

Most people are not looking for one job title. You might be a frontend engineer who also applies to product engineer and full-stack roles, each with a different resume.

So there is no list to pick from. You type your roles in your own words, on the dashboard's Start tab or during onboarding, and they are saved in `profile/roles.md` with your primary one first. Saving from the dashboard replaces only the list; any notes you added to that file are kept. Then:

- **`roles`** tailors three things to them: the skill areas in your profile table, one live practice exercise per role, and role-specific lines in the screening rubric. It adds to what you have and never wipes it, so you can change roles mid-search.
- **`role resume: [role]`** builds a resume version for one role in `profile/resumes/`, using the same verified facts as your master resume in a different order and emphasis.
- **`apply`** says which of your roles a posting matches and starts from that role's resume version. Cover notes are written per company and never reused.

The `roles/` folder holds example patterns for six kinds of job (devops, frontend, backend, product, design, data). The AI uses the closest one as a starting point and adapts it, so a "product engineer" gets something between the frontend and product patterns rather than a copy of either. To improve the starting point for a kind of role, edit its folder or add one.

## Company research

`research: [company]` has your AI tool look the company up on the web and write `applications/<company>/research.md`: what they do, size and stage, recent news, how they work, the reported interview process, links to your own experience, questions to ask, red flags, and what it could not find. It appears on the dashboard in that company's folder.

Every fact carries a source and the date it was read, and anything not found is written as "not found" rather than guessed. Research on the people you will meet is limited to their public professional background. The tool needs web access for this: Claude Code and Cursor have it, and Codex may need web search enabled in its settings.

## Interview stories

Behavioural questions ("tell me about a time you...") are answered with stories, and the project keeps a bank of them in STAR form: **S**ituation, **T**ask, **A**ction, **R**esult.

- **`story`** builds one by asking you the questions, one part at a time, and saves it to `profile/stories/`. `story: [title]` practises an existing one: you tell it from memory and it shows what you skipped.
- **`stories`** shows coverage: which of twelve common questions (conflict, failure, ownership, ambiguity, influence, leadership, pressure, feedback, prioritisation, stakeholder, learning, achievement) have a story and which do not. The same list runs in a terminal with `python3 scripts/stories.py`.
- **`mock interview`** asks behavioural questions and checks your answer against the saved story. **`debrief`** records which story you used in a real interview and how it landed.
- The dashboard's **Prep** tab shows every story with its coverage table, for reading the night before.

Stories are stored as short notes to speak from, not scripts to memorise, because a recited answer falls apart on the first follow-up. The script flags six things: a story that is missing a part, has no competency tags, runs over about two and a half minutes, has a result with no number, says "we" more than "I" in the Action, or has never been practised.

## First session, 60 to 90 minutes

The onboarding (`setup`) is an interview in seven steps. It can be stopped and resumed.

1. Your target roles.
2. Your LinkedIn export, or a pasted resume if you have no profile.
3. Your master resume, `profile/resume.md`, built from it.
4. The basics: location, level, salary floor, and what makes a job an automatic no.
5. Tailoring the profile, practice exercises and rubric to your roles.
6. The audit: every resume line gets evidence or gets cut. Expect it to cut things. That is the point.
7. Your first application, on one real posting, start to finish.

## Every day after

- `check in` to plan the day.
- `apply: [company]` for each posting.
- `debrief: [company]` within an hour of any call, while you still remember the questions.
- One gap rep from `progress/weak-spots.md`.
- `linkedin sync` whenever `profile/resume.md` changes.

## List every command

Type `help` (or `commands`) in your AI tool, or run:

```bash
python3 scripts/commands.py
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

It shows every application with its stage, a count per stage, and flags two things: a next action whose due date has passed, and an application with no contact for 21 days. It reads `applications/PIPELINE.md`, so keep that table's column names and use `YYYY-MM-DD` dates. `--file x.md` reads a different pipeline file.

## Export your resume

Type `export resume` or `export resume: [company]`, or run:

```bash
python3 scripts/resume.py                           # the master resume, profile/resume.md
python3 scripts/resume.py acme                      # the tailored one, applications/acme/resume.md
python3 scripts/resume.py --role frontend-engineer  # a role version, profile/resumes/frontend-engineer.md
python3 scripts/resume.py acme --open               # export, then open it
python3 scripts/resume.py --paper a4                # A4 instead of US Letter
python3 scripts/resume.py --file x.md               # any other Markdown file
```

Each run writes three files, a clean `.md`, an `.html` and a `.pdf`, to a folder under `output/resume/`: `general/` for the master, `roles/<role>/`, `companies/<company>/`, or `custom/` for `--file`. Choose one source per run. They are named after the first heading in the resume, for example `Jane-Doe-Resume.pdf`. Accented and non-Latin names are kept as written.

The PDF is printed by a Chromium-based browser you already have (Chrome, Chromium, Edge or Brave). If none is found, open the `.html` file in any browser and use Print, then Save as PDF. The layout is a plain single column with real text, which is what applicant tracking systems read best. Always open the PDF and check it before sending.

## Archive old entries

Type `archive` about once a month, or run:

```bash
python3 scripts/archive.py            # dry run: shows what would move
python3 scripts/archive.py --apply    # moves it
python3 scripts/archive.py --days 14  # 14 day cut-off instead of 30
```

Daily-log entries older than the cut-off move to `progress/_archive/daily-log-<year>.md`. Only sections headed with a date are entries; a section with any other heading stays in the log. Pipeline rows that are Rejected, Withdrawn or No reply and were last touched before the cut-off move to `applications/_archive/PIPELINE-ARCHIVE.md`. Company folders stay where they are. This keeps the files the AI reads every day short.

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
- **The pipeline script is strict about format.** It lists rows with an unknown stage, a date that is not `YYYY-MM-DD`, missing columns or no company name. A row with a bad date cannot be flagged as overdue or stale until you fix it. Renaming a column breaks it.
- **Only two things are flagged.** An overdue next action, and an application in the Applied stage with no contact for 21 days. Silence after an interview is not flagged unless you set a due date.
- **Resume export is basic.** One fixed single-column layout. It handles headings, paragraphs, bullet and numbered lists, bold, italic and links, but not tables, images or columns. The PDF needs a Chromium-based browser, and nothing checks the page count for you.
- **Memory is manual.** Codex and Cursor do not carry memory between sessions, so anything worth keeping has to be written to `notes/`.
- **The audit is only as honest as you are.** The AI cannot check your claims against anything except what you tell it.
- **The AI can still be wrong.** It can misread a posting or score an answer too kindly. Treat scores as a prompt to think, not a verdict.
- **Archiving is manual and by date only.** Nothing reminds you to run it. It skips a closed application with no valid date, and it never moves company folders or old notes.
- **Your data goes to your AI provider.** Whatever the tool reads is sent to that provider under its terms. Check them before adding anything sensitive.
- **The AI tool still needs setting up.** The dashboard opens with a double-click, but Codex, Cursor or Claude Code has to be installed and opened on the folder, and Python has to be present. A non-technical user will want someone beside them for the first session.
- **The Windows launcher is untested.** It was written and checked on a Mac. If it fails, run `py -3 scripts\app.py` in a Command Prompt from the repo folder and report what it prints.
- **The setup checklist reads your files, not your effort.** "Fill in and audit your profile" ticks once the profile header is complete and the audit has recorded at least one claim you must not inflate. It cannot tell a thorough audit from a quick one.
- **The dashboard is for reading.** Apart from the role list, resume export and archiving, it changes nothing. You cannot edit a document, add an application or run a coaching session from it.
- **The dashboard and role tailoring are new.** The page logic was tested with sample data but has had little real use. The role-specific material is written by your AI tool from the example patterns in `roles/`, which come from general knowledge of those interviews rather than a real search in each role. Read what it produces and correct it.
- **Research is only as good as the web search.** The AI can still misread a page or pick up an outdated one. Open the sources for anything you plan to say in an interview. Small private companies often have little public information.
- **The example is one persona.** It shows a product manager's search. The shape carries over to other roles; the details do not.
- **Story checks are mechanical.** The script counts words, numbers and "we" against "I". It cannot tell whether a story is true, interesting or right for the question. The twelve questions are a common set, not a complete one.
- **Several roles means more upkeep.** Each role version of your resume has to be rebuilt when the master changes, and nothing does that for you.
- **Progress numbers depend on the AI logging them.** Practice scores appear only if the AI adds the row to `progress/practice-log.md` at the end of a session.

## Ideas for improvement

- **More role patterns.** Product marketing, UX research, engineering management, QA, customer success, sales. Better still, patterns reviewed by someone who hires for that role.
- **Editing from the dashboard.** Update a pipeline row, tick a rubric item or add a note without opening a file.
- **A richer pipeline view.** Compute the weekly numbers and reply rate automatically, flag silence after interviews, and chart applications over time.
- **Resume templates.** A choice of layouts, a page-count warning, and a `.docx` export for employers that ask for Word.
- **Native commands per tool.** Slash commands for Cursor and Codex that wrap each mode, so the right file is always loaded.
- **More modes.** Offer review and negotiation, networking and referral tracking, recruiter reply drafting, a weekly review.
- **Tested notes per tool.** What actually happens in Codex and Cursor, once someone has run it there.

If you improve it, a pull request to the template is welcome. Keep your personal files out of it.

## Questions

If you have any questions, feel free to ping me on [LinkedIn](https://www.linkedin.com/in/hytonylee). You can also find me at [www.hytonylee.com](https://www.hytonylee.com).

## Do not put in this folder

Secrets, tokens, kubeconfigs, internal hostnames, or anything copied from an employer's systems.
