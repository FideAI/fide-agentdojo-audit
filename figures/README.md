# Reproducible figures

Two measured comparisons are kept separate: fixed-state scoring substitution and unchanged-label population selection. The compatibility recipient-control table appears in INSIGHT.md and derives from compatibility/results/qualification.json.

From the repository root, in a separate Python 3.11 environment:

```sh
uv venv --python 3.11 .figures-venv
uv pip install --python .figures-venv/bin/python -r figures/requirements.lock
.figures-venv/bin/python -B figures/build.py
```

The builder verifies the sealed archive companion and regenerates both charts as PNG, SVG and PDF plus figure-data.json. It uses packaged derived counters, never raw historical payloads. File-byte identity of generated image metadata is not promised. Exact figure values are checked by verify.py; semantic render review remains separate.
