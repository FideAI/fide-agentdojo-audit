# Fide AgentDojo audit

**Unpublished research release candidate. Repository prepared privately; human review and coordinated article release remain pending.**

A reproducible case study of evaluator selection, repair compatibility and evidence filtering in AgentDojo. The same recorded behavior can receive a different score when a different evaluator is selected. Activating an existing correction also changes a scoring rule under older benchmark versions.

- [Insights essay: When fixing the score changes the test](INSIGHT.md)
- [Technical paper](RESEARCH-PAPER.md)
- [Claim ledger](CLAIMS.md)
- [Compatibility experiment](compatibility/README.md)
- [Sources and prior work](docs/SOURCES.md)

The Fide website article is not yet published; this repository's draft is the reading copy. No guessed public article URL or release DOI is provided.

## What the evidence supports

1. A selected 7,400-record screen yields 45 discrepancies reconstructed under the inspected code. An existing upstream correction recognizes all 45; exact historical scoring implementations remain unknown.
2. In a selected 200-record comparison, Fide's evidence filter removes all eight detector-labeled successes. Holding publisher labels fixed, detector/tool-filter counts change from 8/40 versus 1/40 to 0/29 versus 1/29. This is our selection effect, not an upstream concealed result or revised historical leaderboard.
3. Importing and rebuilding registration resolves 25 declaration mismatches across seven task IDs but changes an eighth task's implementation in older versions. An isolated native utility branch changes one verdict. A blanket compatibility-preserving repair is not qualified.

The study applies established auditing and evidence-bounds ideas. The upstream correction belongs to its authors. No model inference was rerun. See the paper for selection, alternative explanations and unresolved results.

## Quick verification (offline, standard library)

```sh
python3 -B verify.py
```

This verifies the release manifest and recomputes counters/relationships from packaged **derived** evidence. It does not establish raw-record correctness or scientific novelty.

## Full reproduction

Requires Git, uv and Python 3.11. Dependency/source acquisition accesses public registries and GitHub; experiments run locally without inference APIs. The pinned upstream checkout is roughly 516 MB. Runtime guards are Python-level protections, not an OS sandbox.

```sh
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python --no-deps --only-binary :all: -r requirements.lock
.venv/bin/python -B archive/acquire.py
.venv/bin/python -B archive/reproduce.py --mode full
.venv/bin/python -B archive/reproduce.py --mode full --classifier amended
.venv/bin/python -B compatibility/reproduce.py
```

Each experiment writes a new ignored run directory and refuses overwrites. Historical tool calls and injection strings are parsed as inert data, never executed. Archive and compatibility results are compared against preserved derived tables. The amended classifier remains explicitly separate from the original algorithm. The compatibility runner expects its internal repair gates to reject blanket qualification.

[Archive details](archive/README.md) explain native fixtures, full recomputation and controls. [Compatibility details](compatibility/README.md) explain source-derived selection, ambiguity, exclusions and isolated utility controls. [Figure instructions](figures/README.md) reproduce charts using a separate rendering environment. [Qualification](QUALIFICATION.md) states what has actually been tested.

## Repository boundaries

`archive/` is the sealed, byte-identical earlier companion with its own hash manifest and historical qualification/status notes. Those historical notes are not the current repository license. `compatibility/` is an adapted portable follow-up. The root release manifest covers both and the current paper, essay, claims and documentation. [Provenance](PROVENANCE.json) identifies inputs and adaptations.

We distribute minimized numerical/Boolean evidence, source locators/hashes, analysis code and figures. Raw historical traces, source checkouts, model-message contents, full third-party papers, private review deliberations, credentials and local run logs are not release contents. [Failure and amendment history](docs/FAILURES-AND-AMENDMENTS.md) retains material negative outcomes without exposing raw private logs.

## Reuse, scrutiny and corrections

Fide-authored release material is licensed under [MIT](LICENSE). Upstream material retains its [MIT notice](LICENSES/AgentDojo-MIT.txt); separately acquired sources and dependencies retain their own terms. See [rights and attribution](RIGHTS.md). An open license is not a claim that every upstream trace is cleared for redistribution.

Use repository issues to identify a disputed claim, source locator, expected behavior and reproduction command. Please do not include credentials, raw personal records or active payloads. [Contributing and corrections](CONTRIBUTING.md) explains how we record substantive changes. AI review is disclosed in [review and limitations](docs/REVIEW.md); independent human review remains pending.
