# Project execution captures

Re-run the three application-security demonstrations and test suites, then
render their actual output into high-resolution PNG terminal captures.

```bash
python3 -m pip install -r tools/project-screenshots/requirements.txt
python3 tools/project-screenshots/capture.py
```

Requirements: Linux, Java 17+ with `jdk.compiler`, Python 3.11+, and the DejaVu
Sans / DejaVu Sans Mono fonts. On Debian or Ubuntu the fonts are provided by
`fonts-dejavu-core`.

Every project receives `docs/assets/execution.png` and a matching
`docs/assets/execution.json` transcript. Programs run in their own project
directory. All commands must exit successfully; a failing command aborts capture.
The script wraps long lines to fit but does not replace or invent program output.

These are rendered CLI output captures, not screenshots of a graphical
application. Measured timings in Python test summaries and recovery output vary
between runs. Project runtime dependencies are unchanged; Pillow is only needed
to regenerate the documentation images.
