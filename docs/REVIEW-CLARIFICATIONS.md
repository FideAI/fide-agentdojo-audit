# Reader-review clarifications

October 13, 2026. A separately supplied AI review prompted a read-only recheck of existing selected records and source. This is not independent human review, a new model evaluation or a full raw reproduction.

## Direct scoring and version dispatch are different tests

The 45 retained original-fail/corrected-pass cases were reconstructed and scored by calling the corrected predicate directly. Of those records, 42 have no benchmark-version value and three report v1.2.1. Loading and rebuilding selects that task-0 correction only under v1.1.2 and later. Neither a missing version nor a version name identifies the exact historical execution environment.

## Why an older rule changes

The pinned loader offers v1.1.2 suites but omits the v1_1_2 module import. Seven of the module’s eight task declarations use versioned updates. UserTask13 uses `register_user_task`; that implementation writes to `(1, 0, 0)`. Loading it replaces the base task rule. Native selection results and the isolated recipient-matching control remain in [the compatibility experiment](../compatibility/README.md). We have not established why the module was left unloaded. Calling the import omitted describes code behavior, not author intent.

## Why the detector records were excluded

All eleven excluded records in the selected detector configuration contain at least one email-send response with the marker `<Data omitted because a prompt injection was detected>`. The pinned detector’s transformation emits that marker. Eight of these eleven records have saved attack-success labels. The other three are not complete-target send cases. The notice therefore explains the missing readable responses without establishing success for all eleven.

This supports an evidence-selection mechanism: the defense transforms a response; an audit requiring the original readable content drops the record. It does not establish malicious concealment, erroneous publisher exclusions or the exact code that ran historically. Fide made the exclusions studied here.

## Reproduce this check

After acquiring the pinned upstream source using the normal reproduction instructions:

```sh
python3 -B tools/review_mechanisms.py --source archive/.local/agentdojo
```

Pass your actual pinned checkout path if different. This reads JSON records as inert data and parses source with Python AST. It checks selected raw-record hashes against the original manifest and inspected source bytes against the pinned Git commit. It does not import upstream Python, run a detector, execute tool calls or contact a model API. Default mode compares against the retained [minimized output](../evidence/review-mechanisms.json); `--write` deliberately replaces that output.

The output contains source paths/hashes, version values, saved Boolean labels, zero-based message indices and static registration expressions. It contains no raw messages or email addresses. The default repository verifier checks these projections against the original selected populations and counts; use the command above to recheck the original bytes.

## Attribution and review status

[Upstream PR #193](https://github.com/ethz-spylab/agentdojo/pull/193), by C01in-0, proposes a related travel-task correction in v1.2.3 while preserving earlier scorers. Its tests and replay claims are author-reported, not independently rerun in this check. Fide’s owner confirmed no connection to that PR or its author on October 13. The source citation credits the specific preceding work without treating it as proof of every intended compatibility contract.

The reviewer’s article criticisms led to revised copy and clearer methods. Human editorial rewrite/signoff and independent human technical review have not been certified. The website’s publication-enabled configuration is a release mechanism, not evidence that those reviews occurred.
