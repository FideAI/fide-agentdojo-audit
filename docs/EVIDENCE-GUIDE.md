# Inspect the evidence

Start with the [worked example](WORKED-EXAMPLE.md) for one concrete record, or use the map below to check a result. **Recorded results, analysis code and review assessments serve different purposes.** A link to a script shows how we computed something; it is not itself a recorded observation.

The JSON files here contain minimized results. They omit message bodies, recipient addresses, raw prompts and local machine paths. The [full reproduction instructions](../README.md#full-reproduction) let you acquire the pinned public source and regenerate the underlying outputs locally.

## Results and their methods

| Question | Recorded evidence included here | Method and reproduction route |
|---|---|---|
| Which 7,400 records were screened? | [Source paths and hashes](../archive/manifests/outcome-cohort.json); [screening outcomes](../archive/data/record-count-inputs.json) | [Screening code](../archive/scripts/outcome/scan_records.py); full archive reproduction |
| Why do 45 of the 75 candidates reproduce the discrepancy? | [All candidate outcomes](../archive/data/adjudication-count-inputs.json); [one worked reconstruction](WORKED-EXAMPLE.md) | [Reconstruction code](../archive/scripts/outcome/adjudicate.py); full archive reproduction writes `outcome/results/adjudication.json` |
| Does loading the correction change task-0 scores? | [24 original registration cells](../evidence/registration-controls.json) | [Registration-control code](../archive/scripts/outcome/registration_test.py); archive reproduction writes `outcome/results/registration.json` |
| What changes on the same 29 tasks? | [Record-level comparison inputs](../archive/data/comparison-count-inputs.json) | [Predicate-comparison code](../archive/scripts/outcome/compare_scores.py); full archive reproduction |
| Which exclusions change the saved-label comparison? | [Comparison inputs with exclusion flags](../archive/data/comparison-count-inputs.json); [event classifications](../archive/data/observability-count-inputs.json) | [Summary code](../archive/scripts/observability/summarize.py); full archive reproduction writes `observability/results/selection-comparison.json` |
| What supports the event-evidence ranges? | [Record-level strict and contract classifications](../archive/data/observability-count-inputs.json) | [Original classifier](../archive/scripts/observability/audit.py); full archive reproduction writes `observability/results/audit-summary.json` |
| Can a later transformation change the saved response? | [12 native controls and nine classifier controls](../evidence/logging-controls.json) | [Native-control code](../archive/scripts/observability/native_controls.py); see the logging explanation below |
| Does the classifier amendment address contradictions? | [13 before/after controls](../evidence/amendment-controls.json) | [Control code](../archive/scripts/observability/amendment_controls.py); [amended classifier](../archive/scripts/observability/audit_amended.py); amended full reproduction checks the unchanged archive projections |
| Does importing the module preserve older task implementations? | [Dispatch comparisons](../compatibility/results/comparisons.json); [changed cells](../compatibility/results/changes.json); [utility-branch results](../compatibility/results/qualification.json); [repair-gate decisions](../compatibility/results/impact-summary.json) | [Compatibility reproduction instructions](../compatibility/README.md) |

All generated archive paths above are relative to the new `archive/runs/<run-id>/` directory printed by the runner. They are not files silently omitted from the release. The [claim ledger](../CLAIMS.md) supplies the limits on each interpretation.

## Reading the compact controls

The registration file contains the original 24 cells: two loading states, three surrounding-email conditions and four actions. Pair rows on `extra` and `action` to see the four changed verdicts. `old_version_preserved` describes that original task-0 control; it does not certify compatibility for other tasks. The later [892-cell-per-arm audit](../compatibility/REPORT.md) addresses that wider question.

The logging projection retains each control's action, transformation mode, abort flag and number of created messages. `final_equals_deep` compares the final tool-message list with a deep copy captured before the transformation. `final_equals_shallow` compares it with the shallow copy; `prelog_equals_deep` checks the logger's earlier on-disk snapshot against the deep copy. Equality includes the whole tool-message objects in the local run; their content is not exported here.

In `goal_send-redact`, one message was created, the final trace differs from the deep copy, and the shallow copy agrees with the final trace. The earlier logger snapshot agrees with the deep copy. In `goal_send-abort`, the send also persists, but the trace is not redacted: abort and replacement are different control paths. These are authored current-code controls, not proof of the path that produced a historical record.

The amendment file retains both `strict` and `contract` classifications before and after the guard. Five contradictory-receipt controls change the contract result from success to unknown. These authored counterexamples do not establish an observed defect in the selected archive; the 200-record archive projections remain unchanged.

## Reproduce the added projections

After completing the [full archive reproduction](../README.md#full-reproduction), substitute its actual run directory below:

```sh
python3 -B tools/project_navigation_evidence.py --run archive/runs/<run-id>
```

The [projection script](../tools/project_navigation_evidence.py) compares four compact files with your local results. It verifies the worked record against the sealed source hash and reads historical messages only as JSON. It performs no inference and executes no trace content. For a nondefault source checkout, add `--source PATH`. `--write` is for deliberately updating the release projections after review; the default only compares them.

The projections matched both existing full reproduction runs, one with each classifier. This is a packaging check on previously obtained results, not a new experiment or independent replication. [Projection provenance](../evidence/PROVENANCE.json) records the original input hashes; timestamp-bearing local outputs can have different hashes on a fresh run even when the minimized results agree.

## What the review links contain

[Review and limitations](REVIEW.md) summarizes AI review scope and unresolved questions. It is not the full reviewer report or a substitute for the evidence above. The expanded 63-cell AI reviewer exercise mentioned in the paper is a historical review result; its full transcript and implementation are not included in this release. The original 24-cell registration experiment and the later compatibility experiment are included and reproducible here.

[Failure and amendment history](FAILURES-AND-AMENDMENTS.md) is also a summary. Original private failure logs, reviewer deliberations and full-text literature snapshots remain outside the package. No link labeled as a result or reconstruction routes to those summaries in their place.
