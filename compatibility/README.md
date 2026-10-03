# Registration and compatibility experiment

This supplement asks whether importing an omitted update changes only the intended scoring rules, or also changes older versions. It is a reproduction and compatibility study at one fixed commit. See [results and interpretation](REPORT.md).

After the root README's dependency setup and upstream acquisition, run from the repository root:

```sh
.venv/bin/python -B compatibility/reproduce.py
```

Optional `--source PATH` selects a clean checkout of the same commit; `--output NEW_DIRECTORY` selects a new output folder. The runner refuses existing outputs, verifies all 100 source files and exact dependencies, and copies its executable scripts into an isolated run. It compares twelve projected result files and the source diff against this repository's preserved outputs. Do not run individual scripts in this directory: they are runtime components staged by the runner.

The runner uses the original algorithms with explicit source injection and fresh output paths. Results omit goal/prompt text, replacing it with hashes; machine paths and raw stack traces are omitted. The comparison is computational reproduction, not independent adjudication. Raw runtime outputs can contain source prompts and machine paths and stay under ignored `runs/`.

Each native worker blocks Python socket/process operations before importing AgentDojo. The outer runner starts its own worker processes. One blocked socket-allocation capability probe is recorded per arm. No historical instruction, agent run or tool ground truth executes. This guard is not an OS sandbox.

The regression decision intentionally exits 1 for every arm: no arm qualifies as a blanket compatibility-preserving repair. The orchestrator expects those refusals and returns 0 when the observations reproduce. Native selection follows the maximum registered compatible version correctly; the finding concerns registration availability and an older-version replacement.

[PROTOCOL.md](PROTOCOL.md) and [AMENDMENT.md](AMENDMENT.md) preserve original text and timestamps. The latter followed the dispatch results and specified the isolated branch controls. These are internal timestamped commitments with disclosed prior exposure, not externally preregistered or blinded work. [Failure history](../docs/FAILURES-AND-AMENDMENTS.md) preserves material corrections and nulls.
