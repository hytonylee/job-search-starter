# Mode: export resume

`export resume` exports the master resume. `export resume: [company]` exports that company's tailored one. For a role version, run `python3 scripts/resume.py --role [name]`. Reads: nothing.

1. Run `python3 scripts/resume.py` or `python3 scripts/resume.py [company]`. Add `--paper a4` if I am applying outside North America.
2. Show me the paths it printed. The files land in `output/resume/general/` or `output/resume/[company]/` as `.md`, `.html` and `.pdf`.
3. If the PDF was not created, tell me to open the `.html` file in a browser and use Print, then Save as PDF.
4. Ask me to open the PDF and check the page count and line breaks before I send it. You cannot see the PDF.

## Rules

- Never edit files in `output/`. To change the resume, edit the source `.md` and export again.
- The script supports headings, paragraphs, bullets, bold, italic, links and rules. If the source uses a table or an image, rewrite that part as plain lines first.
