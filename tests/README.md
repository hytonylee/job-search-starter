# Tests

Checks for the scripts in `scripts/`. They need Python 3.8+ and nothing else, and they work on temporary copies, never on your files.

```bash
python3 -m unittest discover -s tests
```

Run them after changing a script. Your AI tool does not need to read this folder in normal sessions.
