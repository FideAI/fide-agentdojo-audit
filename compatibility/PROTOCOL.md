# Prospective bounded registration-contract audit

Internal protocol; authored before generating the new dispatch inventory or examining its outcomes. This follows extensive exposure to the known task-0 omission, the 45-case results, original registration script, expanded reviewer summary, loader source, and version-selection helper. It is neither independent preregistration nor a blind/unseen holdout. The new author is a fresh-context Codex AI agent within the same orchestrated session.

## Decision and question

Closest-work reading already establishes cardinality failures, content witnesses, receipt-based public-trace reconstruction, and evidence-based unknowns/bounds. No inspected closest source describes the particular omitted-module dispatch inventory. A larger archived cohort cannot resolve historical runtime and would not add a distinct method. Choose ONE follow-up: a complete, source-derived identity regression audit of the pinned default-suite version-selection contract, with a minimal import intervention. Do not expand into new inference or archive sampling.

Question: does the default loader resolve every declared task override consistent with its per-suite version target and the upstream max-compatible-version rule, and does supplying the omitted import repair identity selection without altering earlier versions or task membership?

Contract has two separately reported levels: (A) explicit operational rule in get_version_compatible_items and update_* docstrings: maximum registered version <= suite.benchmark_version. (B) research expectation that shipped decorated overrides for a named default version are meant to be registered by its default loader. B is supported by the loader's registration comments and v1.1.2 snapshot but remains an interpretation of intent. Never treat source-file presence alone as an unconditional promise or historical deployment proof. Honor actual per-suite targets declared in loader, not the nominal version string. Superseded overrides and targets below an override are intentional exceptions, not defects.

## Selection and held-fixed variables

Pin 089ed468cf3ed0322acc66b0211f26d9d90dbf60, existing qualified Python 3.11 environment. Enumerate every top-level task class decorated with register_user_task/register_injection_task/update_user_task/update_injection_task under src/agentdojo/default_suites; include supported loader versions and four default suites. Unsupported syntax, duplicate definitions, missing baseline IDs, ambiguous suite binding or undocumented targets are explicit exclusions/errors, not silently inferred.

Independently implement static AST extraction of class/module/decorator version and explicit loader per-suite targets. Do not reuse upstream compatibility helper for oracle. Compare native selected task class module/name/source hashes in fresh processes to this frozen source-derived expectation. Run three arms: default; late import with prebuilt snapshots; omitted-module import followed by loader rebuild. No task goals, predicate bodies, state fixtures or historical records are changed. All native activity remains local imports, task-object construction and introspection; no task ground truths, tool calls, archived payloads or model calls execute.

## Counterhypotheses and falsification

H0: all expected selections already match; known omission may be a task-local or intentionally dormant correction. H1: distinct omissions/supersessions make a general missing-import story inaccurate. H2: one import plus rebuild resolves selections while preserving version boundaries. H3: that import activates additional task semantics or changes task membership/goals, making it unsuitable as a drop-in behavioral repair.

Falsify a broad registration-failure claim if no discrepancy remains after correctly respecting per-suite targets. Falsify an isolated task-0-repair claim if other selected class identities change. Falsify a blanket repair recommendation if task IDs, goals/prompts, or unrelated classes change, or if import intervention fails contract matching. Even perfect identity agreement does NOT validate the changed task semantics.

## Controls and analysis

Report exact cells and unique task/version identities, not a defect prevalence or independent trials. Preserve all native exceptions. Compare class identity, source file SHA, definitions and ID sets; native __module__ and inspect.getfile provide a check independent of static parser. Below-boundary versions must remain identical. Same-suite no-override tasks and unaffected banking/slack tasks provide negative controls. Add one authored wrong expected module and one deliberately too-early version as oracle-detection controls; they must be detected. Distinguish declaration parity from runtime registered-only parity to avoid proving the parser by itself. Report inherited versus locally defined GOAL/PROMPT where changed identities select different text.

## Stop rules

Stop after this pin, these three arms, static/native comparison and controls. At most two implementation-repair retries; retain failed scripts/logs and explain deviations. If parser coverage is incomplete, report qualification failure rather than broad claims. No benchmark/model inference, external writes, outreach or patch to frozen source. Acquisition uses public official sources separately. Offline run denies sockets/process launches after runner-created workers start; record and deliberately test the network block. No outcome-based expansion.

## Planned outputs

Source/input manifests with hashes; exact commands; protocol timestamp/hash before first inventory; independently authored scripts; arm JSON; discrepancy and summary JSON; negative-control results; REPORT.md with prior-work subtraction, strongest objection, publishing assessment and precise proposed manuscript patches. Source text snapshots remain private working evidence; no rights clearance is asserted.
