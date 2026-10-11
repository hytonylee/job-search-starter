# Job Search Starter

A folder of plain text files that turns an AI coding tool (Codex, Cursor or Claude Code) into a job-search coach that remembers your history. The AI reads `AGENTS.md` at the start of every session, so it knows who you are, where every application stands, and which gaps real postings have exposed. A local dashboard lets you read all of it in your browser.

## Where this came from

I built the original version of this for my own job search as a product engineer, and kept changing it as I learned what worked. This repo is the reusable part of that setup with everything personal removed.

It began as a setup for a friend looking for a DevOps position and now works for any role, or several at once. You tell it the job titles you are targeting, in your own words, and it shapes itself around them.

## Before you start

You need four things. None of them is included here.

| You need | Why | Notes |
|---|---|---|
| **An AI coding tool**: [Cursor](https://cursor.com), [Codex](https://openai.com/codex) or [Claude Code](https://claude.com/product/claude-code) | It does the coaching and edits the files | These usually need a paid plan or charge for usage. If you have never used one, Cursor is the easiest to start with, because it is an ordinary app with a chat panel |
| **Python 3.8 or newer** | It runs the dashboard and the small scripts | Free from [python.org/downloads](https://www.python.org/downloads/). Most Macs and Linux machines already have it. On Windows, tick "Add python.exe to PATH" during the install |
| **Your LinkedIn profile, or a resume you can paste** | It is the starting point for your resume | |
| **A GitHub account**, optional | To keep a private backed-up copy | You can also just download the ZIP |

A chat app in a browser is not enough. It cannot see or change the files in this folder, and the whole method depends on the AI working from them.

**Time:** about 10 minutes to get the folder and open the dashboard, then 60 to 90 minutes for the first session. You can stop and pick it up later.

## Quick start

1. **Get your own copy.**
   - With GitHub: click **Use this template**, create your copy, and **make it private**. It will hold your resume, salary floor and interview notes. Then clone your copy to your computer (GitHub Desktop works if you prefer not to use a terminal).
   - Without GitHub: click **Code → Download ZIP** and unzip it somewhere you will find again. Nothing is backed up this way, so keep your own copy of the folder.
   - Either way, work in your own copy, not directly in this repo, so your personal files never end up here.
2. **Open the dashboard.** In the `start/` folder, double-click `Open dashboard (Mac).command` or `Open dashboard (Windows).bat`. A page opens in your browser. See [The dashboard](#the-dashboard) if it does not.
3. **Look at the example.** Press **See an example** at the top of the page to see what a working project looks like, then **Back to my data**.
4. **Press Start project onboarding.** The box that opens shows where this folder is on your computer, how to open it in your AI tool, and a first message to paste.
5. **Paste the message into your AI tool.** It asks you a series of questions and sets the project up one step at a time. The dashboard fills in as it goes.

If you use **Claude Code**, also create a file named `CLAUDE.md` in the folder containing the single line `@AGENTS.md`. Codex and Cursor read `AGENTS.md` without that.

**Do not put in this folder:** passwords, access tokens, customer data, or anything copied from an employer's systems.

## How it works

Everything serves one loop:

1. **Seed.** Your LinkedIn export, or a pasted resume, becomes your master resume.
2. **Audit.** Every resume line gets evidence or gets cut.
3. **Apply.** Each real posting gets a folder, a fit score, a tailored resume and a row in the pipeline.
4. **Prepare.** Company research, interview stories and practice exercises for the roles you are targeting.
5. **Collect gaps.** Every posting and every interview adds evidence to a ranked gap list.
6. **Plan the day.** From the pipeline and the gap list, not from mood.
7. **Sync LinkedIn.** The resume is the source and the profile is a copy.

You work by typing a **keyword** to your AI tool, such as `check in` or `apply: acme`. Each keyword has its own instruction file, so the AI follows the same steps every time. The dashboard is where you read the results.

## The first session

The onboarding (`setup`) is an interview in seven steps. It checks your files first, so if you stop partway it resumes where you left off.

1. Your target roles.
2. Your LinkedIn export (on LinkedIn: your profile, then **Resources → Save to PDF**, saved as `profile/linkedin-export.pdf`), or a pasted resume if you have no profile.
3. Your master resume, `profile/resume.md`, built from it.
4. The basics: location, level, salary floor, and what makes a job an automatic no.
5. Tailoring the profile, practice exercises and screening rubric to your roles.
6. The audit: every resume line gets evidence or gets cut. Expect it to cut things. That is the point.
7. Your first application, on one real posting, start to finish.

## Every day after

- `check in` to plan the day.
- `apply: [company]` for each posting.
- `research: [company]` before you talk to anyone there.
- `debrief: [company]` within an hour of any call, while you still remember the questions.
- One rep on your top gap, and one `story` or `practice` session when an interview is coming.
- `linkedin sync` whenever your master resume changes.

## Keywords

Type these to your AI tool. `help` prints this list at any time.

| Keyword | What it does |
|---|---|
| `help` (or `commands`) | Lists every keyword and script command |
| `setup` | The onboarding interview, in seven steps |
| `roles` | Tailors your profile, practice exercises and rubric to your target roles |
| `audit` | Checks every resume line for evidence |
| `apply: [company]` | Screens a posting, checks fit, tailors the resume, tracks it |
| `research: [company]` | Looks the company up on the web, with sources |
| `check in` | Daily standup and plan |
| `pipeline` | Shows every application and its status |
| `gaps` | Re-ranks your gaps by evidence and names the top two |
| `drill: [topic]` | Five scored questions on one topic |
| `practice` (or `practice: [role]`) | The live exercise for one of your target roles |
| `story` (or `story: [title]`) | Builds a new interview story, or practises an existing one |
| `stories` | Shows which common interview questions have a story |
| `mock interview` | A full interview round for a company in your pipeline |
| `debrief: [company]` | Logs a real interview while you remember it |
| `linkedin sync` | Gives you the text to update your LinkedIn profile |
| `role resume: [role]` | Builds the resume version for one target role |
| `export resume` | Exports a resume to PDF. Add `: [company]` or `: role [name]` for a specific one |
| `archive` | Moves old log entries and closed applications out of the way |

The word is `help`, not `/help`, because `/help` is already a built-in command in most of these tools.

## The dashboard

A local web page for reading your material, so you are not limited to a chat window.

**To open it, double-click the launcher in the `start/` folder:**

| Your computer | Double-click |
|---|---|
| Mac | `start/Open dashboard (Mac).command` |
| Windows | `start/Open dashboard (Windows).bat` |

A small window opens and stays open while the dashboard runs, and the page appears in your browser at `http://127.0.0.1:8765/`. To stop it, close that window. If you double-click again while it is running, it opens the one already running instead of starting a second. If that port is taken by another program, it uses the next free one and says which. On Linux, or if you prefer a terminal, run `python3 scripts/app.py` from the repo folder.

It runs only on your own computer and sends nothing anywhere. That also means the address works only on your machine: it is not a link you can send to someone else.

If the launcher does not start:

- **"Python 3 is not ready" (Mac) or "Python 3.8 or newer was not found" (Windows).** Install Python from [python.org/downloads](https://www.python.org/downloads/). On Windows, tick "Add python.exe to PATH" during the install. On a Mac, macOS may instead offer to install Apple's developer tools, which include Python: accept, wait for it to finish, and double-click again.
- **Mac says the file cannot be opened, or is from an unidentified developer.** This happens if you downloaded the ZIP. Open **System Settings → Privacy & Security**, scroll down, and click **Open Anyway** next to the file's name. On older versions of macOS, right-click the file and choose Open instead. You only need to do this once.
- **Mac says you do not have permission.** In Terminal, run `chmod +x "start/Open dashboard (Mac).command"` from the repo folder.
- **Windows shows "Windows protected your PC".** Click More info, then Run anyway.

| Tab | What you see |
|---|---|
| **Start** | The onboarding button (it explains how to get an AI tool, shows where this folder is on your computer and how to open it, and gives the first message to paste), a setup checklist that ticks itself off, and your target roles |
| **Pipeline** | Counts per stage, what needs attention, and every application with its fit score, in a table you can sort by clicking a column heading |
| **Applications** | One company at a time: the posting, your fit, the tailored resume, research, interview notes, and a PDF export button |
| **Prep** | Your profile, master resume and role versions, interview stories with their coverage, gap list, practice exercises and every interview question you have logged, formatted for reading before an interview. A document that is still an empty template says what will fill it |
| **Progress** | Applications sent, interviews reached, offers, questions with a story, a funnel diagram, practice scores over time, and recent sessions. Totals count each application once, include archived ones, and go by the furthest stage it reached |
| **Tools** | Export of the master resume or a role version, archiving with a preview, every keyword with a copy button, and a short glossary of the terms used here |

**See an example.** A new project is empty, so the dashboard has a **See an example** button. It switches every tab to a fictional candidate, Sam Rivera, seven weeks into a product management search: a pipeline with follow-ups due, tailored applications, company research, STAR stories and practice scores. It is read-only and kept in its own `example/` folder, so it never mixes with your files and your AI tool never reads it. Press **Back to my data** to return. You can delete the folder, and the button goes with it.

**It updates by itself.** The page reads your files and shows them. When the AI changes a file, the page picks it up within a few seconds, or as soon as you switch back to it. It holds off while you are typing, have unsaved roles, or have an archive preview open, and says so next to the **Refresh** button. To change a document, edit the file or ask the AI: apart from the role list, resume export and archiving, the dashboard changes nothing.

**The funnel.** The Progress tab draws one bar per stage, from Sent to Offer. Each bar is as long as the share of your sent applications that reached that stage, and is split by what happened next: moved on, still open, rejected, withdrawn or no reply. It is built from your own pipeline and its archive, so it fills in as you apply and never needs updating by hand. It relies on the Furthest column: a closed application with no Furthest value is shown as stopping right after it was sent, and the diagram says how many of those there are.

## Your target roles

Most people are not looking for one job title. You might be a frontend engineer who also applies to product engineer and full-stack roles, each with a different resume.

So there is no list to pick from. You type your roles in your own words, on the dashboard's Start tab or during onboarding, and they are saved in `profile/roles.md` with your primary one first. The list sits between two marker lines in that file. Saving from the dashboard replaces only what is between them, so any notes you add elsewhere in the file are left exactly as they are. Then:

- **`roles`** tailors three things to them: the skill areas in your profile table, one live practice exercise per role, and role-specific lines in the screening rubric. It adds to what you have and never wipes it, so you can change roles mid-search.
- **`role resume: [role]`** builds a resume version for one role in `profile/resumes/`, using the same verified facts as your master resume in a different order and emphasis.
- **`apply`** says which of your roles a posting matches and starts from that role's resume version. Cover notes are written per company and never reused.

That gives three levels of resume: one **master** with every verified fact, one **version per role**, and one **tailored copy per company**. If you fix a fact in the master, rebuild the role versions with `role resume: [role]`.

The `roles/` folder holds example patterns for six kinds of job (devops, frontend, backend, product, design, data). The AI uses the closest one as a starting point and adapts it, so a "product engineer" gets something between the frontend and product patterns rather than a copy of either. To improve the starting point for a kind of role, edit its folder or add one.

## Company research

`research: [company]` has your AI tool look the company up on the web and write `applications/<company>/research.md`: what they do, size and stage, recent news, how they work, the reported interview process, links to your own experience, questions to ask, red flags, and what it could not find. It appears on the dashboard in that company's folder.

Every fact carries a source and the date it was read, and anything not found is written as "not found" rather than guessed. Research on the people you will meet is limited to their public professional background. The tool needs web access for this: Claude Code and Cursor have it, and Codex may need web search enabled in its settings.

## Interview stories

Behavioural questions ("tell me about a time you...") are answered with stories, and the project keeps a bank of them in STAR form: **S**ituation, **T**ask, **A**ction, **R**esult.

- **`story`** builds one by asking you the questions, one part at a time, and saves it to `profile/stories/`. `story: [title]` practises an existing one: you tell it from memory and it shows what you skipped.
- **`stories`** shows coverage: which of twelve common questions (conflict, failure, ownership, ambiguity, influence, leadership, pressure, feedback, prioritisation, stakeholder, learning, achievement) have a story and which do not.
- **`mock interview`** asks behavioural questions and checks your answer against the saved story. **`debrief`** records which story you used in a real interview and how it landed.
- The dashboard's **Prep** tab shows every story with its coverage table, for reading the night before.

Stories are stored as short notes to speak from, not scripts to memorise, because a recited answer falls apart on the first follow-up. Six things are flagged automatically: a story that is missing a part, has no competency tags, runs over about two and a half minutes, has a result with no number, says "we" more than "I" in the Action, or has never been practised.

## Three things that make it work

1. **Keep everything in this folder.** A browser chat cannot see these files, so it fills the holes with confident guesses.
2. **Add rules as you learn, in the right file.** When you notice a pattern in how you fail (rambling, vague answers, skipping follow-ups), write it into the mode file where it applies, such as `modes/drill.md`. The rules that help most are the ones you add yourself.
3. **Let postings choose what you study.** After 5 to 10 applications the same missing skill will show up again and again. Study that, not a roadmap.

## What is in the repo

```
AGENTS.md            the index the AI reads every session
README.md            this file
profile/             who you are: target roles, profile, master resume, a resume version per role, interview stories, LinkedIn text
modes/               one instruction file per keyword
applications/        the pipeline, the screening rubric, one folder per company
progress/            daily log, practice log and the ranked gap list
notes/               long-term memory, one fact per file
tests/               checks for the scripts (run them after changing one)
roles/               example patterns the AI adapts to your roles (devops, frontend, backend, product, design, data)
scripts/             dashboard, pipeline viewer, resume export, story coverage, archiving, command list
ui/                  the dashboard page
start/               double-click launchers for the dashboard (Mac and Windows)
example/             a fictional candidate for the dashboard's "See an example" view
output/              generated files: pipeline page, exported resumes (not committed)
```

Only `AGENTS.md` and `README.md` sit at the top level, apart from git's own dotfiles and, if you use Claude Code, a one-line `CLAUDE.md` pointer. Source files live in their folders, and anything a script generates goes to `output/`. Old entries move to `_archive/` folders inside `progress/` and `applications/`.

**Keeping it cheap to run.** `AGENTS.md` is loaded into every session, so it stays a short index of about 400 words: the keywords on one line, where files live, and seven rules. Each keyword has its own file in `modes/`, which the AI opens only when you type that keyword. Keep it that way: new detail goes in a mode file, `profile/profile.md` or `notes/`, never in `AGENTS.md`. Start a fresh session for each task instead of running one long one.

## Scripts, for the terminal

Everything below can also be done from the dashboard or by typing a keyword to the AI. The scripts need Python 3.8 or newer and nothing else to install. On Windows, type `py -3` in place of `python3`.

**List every command**

```bash
python3 scripts/commands.py
```

Prints every keyword and every script command. The list is built from the keyword list in `AGENTS.md`, the `Purpose:` line of each mode file and each script's own usage text, so it stays current when you add your own.

**See your pipeline**

```bash
python3 scripts/pipeline.py               # table in the terminal
python3 scripts/pipeline.py --html        # also writes output/pipeline.html
python3 scripts/pipeline.py --open        # writes the page and opens it in your browser
python3 scripts/pipeline.py --file x.md   # reads a different pipeline file
```

Shows every application with its stage, a count per stage, and flags two things: a next action whose due date has passed, and an application with no contact for 21 days. It reads `applications/PIPELINE.md`, so keep that table's column names and use `YYYY-MM-DD` dates.

Each row carries a **Fit** score, written like `4/5`: the number of the posting's required items you meet with evidence, out of the number it lists. `apply` works it out and records it, and the dashboard colours it green from 70%, amber from 50% and grey below, matching the screening rubric's apply-or-skip thresholds.

The stages are Drafted, Applied, Screen (the first call), Interview (any round after that), Final and Offer, and a row is closed as Rejected, Withdrawn or No reply. When a row is closed, its **Furthest** column records the stage it had reached, so an interview or an offer still counts in your totals after a rejection.

**Export a resume**

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

**Check your stories**

```bash
python3 scripts/stories.py
```

Lists your stories, which of the twelve questions have none, and what to fix in each.

**Archive old entries**

```bash
python3 scripts/archive.py            # dry run: shows what would move
python3 scripts/archive.py --apply    # moves it
python3 scripts/archive.py --days 14  # 14 day cut-off instead of 30
```

Daily-log entries older than the cut-off move to `progress/_archive/daily-log-<year>.md`. Only sections headed with a date are entries; a section with any other heading stays in the log, and everything that stays keeps its place. Pipeline rows that are Rejected, Withdrawn or No reply and were last touched before the cut-off move to `applications/_archive/PIPELINE-ARCHIVE.md`. Company folders stay where they are. This keeps the files the AI reads every day short.

**Run the tests**

```bash
python3 -m unittest discover -s tests
```

Checks the scripts against temporary copies, never your files. Run it after changing a script.

## Limitations

**How proven it is**

- **It comes from one person's search.** The rules reflect what one product engineer needed. Some will not fit you, and your own failure patterns are not in here yet.
- **This cleaned-up version is new.** The method was used for a real search in Claude Code. This template has not yet been run end to end in Codex or Cursor.
- **The dashboard and role tailoring are new.** The page logic was tested with sample data but has had little real use. The role-specific material is written by your AI tool from the example patterns in `roles/`, which come from general knowledge of those interviews rather than a real search in each role. Read what it produces and correct it.
- **The Windows launcher is untested.** It was written and checked on a Mac. If it fails, run `py -3 scripts\app.py` in a Command Prompt from the repo folder and report what it prints.

**What it does not do**

- **It does not find jobs.** You bring the postings. There is no job-board search, scraping or auto-apply.
- **Very little is automated.** The pipeline is a Markdown table the AI edits, and the scripts only display it. LinkedIn is updated by hand, and there are no reminders. If you skip `check in`, nothing nudges you.
- **The dashboard is for reading.** You cannot edit a document, add an application or run a coaching session from it.
- **Setup still takes some comfort with new tools.** The dashboard opens with a double-click and walks you through getting an AI tool and opening the folder in it, but those steps happen in tools this project does not control. Someone who has only used chat apps may want a person beside them for the first session.
- **Memory is manual.** Codex and Cursor do not carry memory between sessions, so anything worth keeping has to be written to `notes/`.

**Where the AI can let you down**

- **Mode files rely on the AI following a pointer.** If a keyword runs without its rules, tell the tool directly: "follow `modes/apply.md`."
- **The audit is only as honest as you are.** The AI cannot check your claims against anything except what you tell it.
- **The AI can still be wrong.** It can misread a posting or score an answer too kindly. Treat scores as a prompt to think, not a verdict.
- **Research is only as good as the web search.** The AI can misread a page or pick up an outdated one. Open the sources for anything you plan to say in an interview. Small private companies often have little public information.
- **Your data goes to your AI provider.** Whatever the tool reads is sent to that provider under its terms. Check them before adding anything sensitive.

**Mechanical limits**

- **The pipeline is strict about format.** It lists rows with an unknown stage, a date that is not `YYYY-MM-DD`, missing columns or no company name. A row with a bad date cannot be flagged as overdue or stale until you fix it. Renaming a column breaks it.
- **Only two things are flagged.** An overdue next action, and an application in the Applied stage with no contact for 21 days. Silence after an interview is not flagged unless you set a due date.
- **Resume export is basic.** One fixed single-column layout. It handles headings, paragraphs, bullet and numbered lists, bold, italic and links, but not tables, images or columns. The PDF needs a Chromium-based browser, and nothing checks the page count for you.
- **Several roles means more upkeep.** Each role version of your resume has to be rebuilt when the master changes, and nothing does that for you.
- **Story checks are mechanical.** They count words, numbers and "we" against "I". They cannot tell whether a story is true, interesting or right for the question. The twelve questions are a common set, not a complete one.
- **The setup checklist reads your files, not your effort.** "Fill in and audit your profile" ticks once the profile header is complete and the audit has recorded at least one claim you must not inflate. It cannot tell a thorough audit from a quick one.
- **Progress numbers depend on the AI logging them.** Practice scores appear only if the AI adds the row to `progress/practice-log.md` at the end of a session. Interview and offer totals rely on the Furthest column being filled in when a row is closed; interview notes in a company folder act as a backstop.
- **The tests cover the scripts, not the page or the AI.** The dashboard page and the mode files have no automated checks.
- **Archiving is manual and by date only.** Nothing reminds you to run it. It skips a closed application with no valid date, and it never moves company folders or old notes.
- **The example is one persona.** It shows a product manager's search. The shape carries over to other roles; the details do not.

## Ideas for improvement

- **More role patterns.** Product marketing, UX research, engineering management, QA, customer success, sales. Better still, patterns reviewed by someone who hires for that role.
- **Editing from the dashboard.** Update a pipeline row, tick a rubric item or add a note without opening a file.
- **A richer pipeline view.** Compute the weekly numbers and reply rate automatically, flag silence after interviews, and chart applications over time.
- **Resume templates.** A choice of layouts, a page-count warning, and a `.docx` export for employers that ask for Word.
- **Native commands per tool.** Slash commands for Cursor and Codex that wrap each mode, so the right file is always loaded.
- **More modes.** Offer review and negotiation, networking and referral tracking, recruiter reply drafting, a weekly review.
- **More examples.** A second fictional candidate in an engineering role, and screenshots of the dashboard in this README.
- **Tested notes per tool.** What actually happens in Codex and Cursor, once someone has run it there.

If you improve it, a pull request to the template is welcome. Keep your personal files out of it.

## Questions

- If you have any questions, feel free to ping me on [LinkedIn](https://www.linkedin.com/in/hytonylee). 
- You can also find me at [www.hytonylee.com](https://www.hytonylee.com).
