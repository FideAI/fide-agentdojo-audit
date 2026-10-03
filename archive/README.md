# AgentDojo evaluation-integrity companion

**Private reproduction candidate. No publication or export approval.** This directory is a portable copy of selected evidence and adapted analysis code. Frozen exploratory studies remain unchanged in the originating private workspace. The existing AgentDojo correction belongs to its upstream authors; this package does not claim novelty or independent human review.

## One safe verification command

From this directory, with Python 3.11 available:

```sh
python3.11 -B verify.py
```

This uses only Python's standard library, runs offline, verifies package file hashes, and recomputes counters from **packaged derived tables**. It does not acquire sources, execute AgentDojo, independently inspect raw records, certify the classifications, or establish historical runtime identity. A successful result means the packaged tables are internally consistent with the specified counters. It makes no model, email, provider, or network calls and writes nothing by default. `--output NEW_FILE.json` saves a new result without replacing an existing file.

The original reconstruction and newer coverage-sensitive classifications remain separate. For example, repeat-prompt's original matched reconstruction is 4→5 / 29; that is not a claim that all 29 records are resolved by the extension's stricter evidence standard. `verify.py` prints separate shared strict bounds and full strict/contract bounds. Full-set detector 8 versus tool-filter 1 and common-subset detector 0 versus tool-filter 1 use unchanged publisher labels.

## Optional clean setup and native reproduction

Requirements: Git, `uv`, Python 3.11, and an ordinary platform supported by the exact dependency wheels. Setup accesses the public source repository and Python package index. Runtime is offline. No sibling repository or preexisting study environment is required.

```sh
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python --no-deps --only-binary :all: -r requirements.lock
.venv/bin/python -B acquire.py
.venv/bin/python -B reproduce.py --mode fixtures
```

`acquire.py` fetches exactly commit `089ed468cf3ed0322acc66b0211f26d9d90dbf60` from `https://github.com/ethz-spylab/agentdojo.git`, checks a clean checkout and the upstream license hash, and refuses an existing destination. The default source destination is `.local/agentdojo`; `--destination NEW_DIRECTORY` is available. Pass the same custom directory as `reproduce.py --source DIRECTORY` if used. The full upstream repository includes raw traces (roughly 516 MB in the qualified local checkout); these are local inputs, **not packaged exports**. Acquisition does not run repository scripts, model instructions, or historical tool calls.

`requirements.lock` retains every exact version from the frozen study dependency list, minus its nonportable editable source entry. Installation uses `--no-deps`: it cannot substitute a newly resolved graph. This is a version lock, **not a hash-locked wheel archive or cross-platform guarantee**. AgentDojo is imported directly from the verified source tree, with no editable installation or unpinned build backend. Upstream logger package metadata can say `unknown` because the source is not installed as a distribution; the validation report records the authoritative commit pin separately. Dependency packages are not vendored.

The fixture runner creates a new UUID-named `runs/` directory, starts each experiment in a separate process, checks dependency versions and all packaged upstream source hashes, and installs a socket/subprocess guard before importing native AgentDojo code. It executes only authored in-memory fixture operations: 48 mechanism cells, 24 registration cells, two task-5 scope pairs, 12 native logging cells, and nine classifier controls. These simulated email operations mutate fixture objects; no email is delivered. The guard is a defense against accidental Python networking, not an OS security sandbox for arbitrary hostile code. This runner does not execute untrusted recorded code.

For an optional full analysis of acquired archives as inert JSON/YAML data:

```sh
.venv/bin/python -B reproduce.py --mode full
```

This additionally regenerates the 7,400-record screen, 75 reconstructions, 200-record matched comparison, and 200-record observability classification in the new output directory. Historical calls are parsed as data and never replayed. The runner checks all 7,400/200 raw hashes and exact equality of the four minimized derived tables. It reuses adapted original analysis logic, so it is **a fresh computational rerun, not independently implemented scientific adjudication**. `--output NEW_DIRECTORY` selects a new output tree; an existing tree is refused. Raw regenerated results and native logs stay in that private run and are not allowlisted for export.

## Separately amended classifier

The original classifier can accept a matching non-error call under the native contract even when its readable receipt contradicts the expected sender, recipient, subject, body or status. The private review found this defect in authored controls; no selected archive verdict changed. `audit.py` preserves the frozen algorithm and remains the archive-reproduction default. `audit_amended.py` is an explicitly separate revision that rejects such a contradictory witness, with thirteen additional authored controls run in both reproduction modes. These controls change five contradiction cases from contract success to unknown, preserve the valid receipt and redacted explicit-null cases, and retain uncertainty for errors, missing fields, unknown arguments and broken pairing.

```sh
.venv/bin/python -B reproduce.py --mode full --classifier amended
```

This writes a separate fresh run and checks the same minimized archived tables. It does not silently alter historical results. The twelve native logging cells and original nine classifier controls still exercise the frozen module; the thirteen amendment controls compare both modules. The amendment does not establish completeness or historical semantics.

## Contents and provenance

- `EXPORT-MANIFEST.json` is the exact export allowlist with hashes. It does not include itself in its hash list; it is copied separately by `export.py`. Hashes detect accidental mismatch, not authenticity against a malicious publisher.
- `data/` contains field-allowlisted rows and Boolean reductions: no message content, raw tool arguments, receipt text or free-text error strings.
- `manifests/` contains relative source paths/hashes, original-to-copy provenance, and selected code hashes. Original paths are workspace-relative provenance references, not runtime requirements.
- `scripts/project.py` defines the lossy projections. Only source locators, identifiers, scores, counts and derived evidence classifications are retained.
- `scripts/outcome/` and `scripts/observability/` retain selected original algorithms. `probe.py` and `common.py` replace hardcoded paths with the isolated execution context. Details and original/copy hashes are in `manifests/provenance.json`.
- `QUALIFICATION.json` records actual fresh-directory checks and limitations; `RIGHTS.md` records unresolved export questions.

To create another private copy without runtime directories, use `python3.11 -B export.py NEW_DIRECTORY`. It copies only the verified allowlist; it never automatically includes `.local/`, `.venv/`, `runs/`, raw archives, private review notes or environment files. This command prepares a private artifact; it does not approve or publish it.

The package does not reproduce paid inference, historical model executions, the neural detector, a corrected historical leaderboard, historical source identity, real-world delivery, or trace completeness. Authored controls qualify narrow mechanisms and analysis rules, not population error rates.
