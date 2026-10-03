# Activating a correction also changes an older evaluator

At AgentDojo commit `089ed468cf3ed0322acc66b0211f26d9d90dbf60`, a static parser enumerates 184 top-level decorated declarations, producing 815 version/suite/task entries. Each native arm observes 892 selected entries across four suites and seven supported version names.

| Arm | Declaration matches | Unambiguous mismatches | Ambiguous entries | Native entries changed from default |
|---|---:|---:|---:|---:|
| Default | 769 | 25 | 21 | 0 |
| Late import | 769 | 25 | 21 | 2 |
| Import and rebuild | 794 | 0 | 21 | 32 |

The 25 mismatches span seven unique task IDs repeated across versions. Rebuilding also replaces workspace UserTask13 across all seven versions, producing 32 changes across eight IDs. Late import alone replaces that task in v1 and v1.1, which share the base suite. The versioned file registers it in the baseline slot. The explicit maximum-registered-compatible-version rule is satisfied in all 892 entries per arm. Expecting every shipped version override to be loaded remains a research interpretation of the source, not proof of maintainer intent.

The 21 ambiguous entries come from three duplicate baseline task declarations over seven versions. The 77 generated/composed native entries outside the static parser remain in the before/after comparison and do not change. Task membership, prompts, goals and ground-truth method text remain unchanged; public prompt/goal hashes allow identity comparison without redistributing that prose.

UserTask13's replacement lowercases email recipients before comparison. With unrelated file-change and email-change checks fixed true, the native methods give:

| Authored recipient input | Before import | After late import |
|---|---|---|
| Expected lowercase address | true | true |
| Expected uppercase address | false | true |
| Unrelated address | false | false |

This is an isolated utility branch, not a full task run or a new agent outcome. Normalization may be beneficial, but the same old version name can select a different rule. The regression gate rejects a blanket compatibility-preserving repair. Warm-cache/import-order variants beyond these arms and full semantic correctness of every altered task remain untested.

Inspect [all comparisons](results/comparisons.json), [changes](results/changes.json), [impact summary](results/impact-summary.json), [branch and guard controls](results/qualification.json) and [source diff](results/user-task-13.diff). [Prior work](../docs/SOURCES.md) already establishes broader scoring and evidence-selection concerns. Fide's additional result is this measured implementation and compatibility boundary. No priority claim, historical runtime attribution, broad method novelty or defense generalization follows.
